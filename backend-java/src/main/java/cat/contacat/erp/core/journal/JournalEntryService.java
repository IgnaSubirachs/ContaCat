package cat.contacat.erp.core.journal;

import cat.contacat.erp.core.account.Account;
import cat.contacat.erp.core.account.AccountService;
import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.journal.api.JournalEntryRequest;
import cat.contacat.erp.core.journal.api.JournalEntryResponse;
import cat.contacat.erp.core.journal.api.JournalLineRequest;
import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequenceService;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class JournalEntryService {

    private final JournalEntryRepository repository;
    private final CompanyRepository companyRepository;
    private final AccountService accountService;
    private final DocumentSequenceService documentSequenceService;

    public JournalEntryService(
        JournalEntryRepository repository,
        CompanyRepository companyRepository,
        AccountService accountService,
        DocumentSequenceService documentSequenceService
    ) {
        this.repository = repository;
        this.companyRepository = companyRepository;
        this.accountService = accountService;
        this.documentSequenceService = documentSequenceService;
    }

    @Transactional(readOnly = true)
    public List<JournalEntryResponse> list(String companyId, LocalDate startDate, LocalDate endDate) {
        ensureCompanyExists(companyId);
        List<JournalEntry> entries = (startDate != null && endDate != null)
            ? repository.findAllByCompanyIdAndEntryDateBetweenOrderByEntryDateDescEntryNumberDesc(companyId, startDate, endDate)
            : repository.findAllByCompanyIdOrderByEntryDateDescEntryNumberDesc(companyId);
        return entries.stream().map(JournalEntryResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public JournalEntryResponse get(String companyId, String entryId) {
        return JournalEntryResponse.from(findEntry(companyId, entryId));
    }

    @Transactional
    public JournalEntryResponse create(String companyId, JournalEntryRequest request) {
        validateRequest(request);
        Company company = findCompany(companyId);
        DocumentNumber number = documentSequenceService.allocateNext(companyId, "JOURNAL_ENTRY", "A", request.entryDate().getYear());

        JournalEntry entry = new JournalEntry();
        entry.setCompany(company);
        entry.setSequence(buildSequenceReference(number.sequenceId()));
        entry.setEntryNumber(number.number());
        entry.setFormattedNumber(number.formattedNumber());
        entry.setEntryDate(request.entryDate());
        entry.setDescription(request.description().trim());
        entry.setAttachmentPath(normalizeNullable(request.attachmentPath()));
        entry.setStatus(JournalEntryStatus.DRAFT);
        entry.setLines(buildLines(companyId, entry, request.lines()));

        return JournalEntryResponse.from(repository.save(entry));
    }

    @Transactional
    public JournalEntryResponse post(String companyId, String entryId) {
        JournalEntry entry = findEntry(companyId, entryId);
        if (entry.getStatus() == JournalEntryStatus.POSTED) {
            throw new JournalEntryAlreadyPostedException(entryId);
        }
        validateLines(entry.getLines());
        entry.setStatus(JournalEntryStatus.POSTED);
        entry.setPostedAt(OffsetDateTime.now());
        return JournalEntryResponse.from(repository.save(entry));
    }

    private JournalEntry findEntry(String companyId, String entryId) {
        JournalEntry entry = repository.findById(entryId)
            .orElseThrow(() -> new JournalEntryNotFoundException(companyId, entryId));
        if (!Objects.equals(entry.getCompany().getId(), companyId)) {
            throw new JournalEntryNotFoundException(companyId, entryId);
        }
        return entry;
    }

    private Company findCompany(String companyId) {
        return companyRepository.findById(companyId)
            .orElseThrow(() -> new CompanyNotFoundException(companyId));
    }

    private void ensureCompanyExists(String companyId) {
        if (!companyRepository.existsById(companyId)) {
            throw new CompanyNotFoundException(companyId);
        }
    }

    private cat.contacat.erp.core.sequence.DocumentSequence buildSequenceReference(String sequenceId) {
        cat.contacat.erp.core.sequence.DocumentSequence sequence = new cat.contacat.erp.core.sequence.DocumentSequence();
        sequence.setId(sequenceId);
        return sequence;
    }

    private List<JournalLine> buildLines(String companyId, JournalEntry entry, List<JournalLineRequest> requests) {
        List<JournalLine> lines = new ArrayList<>();
        int index = 1;
        for (JournalLineRequest request : requests) {
            Account account = accountService.findAccountByCode(companyId, request.accountCode());

            JournalLine line = new JournalLine();
            line.setJournalEntry(entry);
            line.setAccount(account);
            line.setLineOrder(index++);
            line.setDebit(scale(request.debit()));
            line.setCredit(scale(request.credit()));
            line.setDescription(request.description() == null ? "" : request.description().trim());
            lines.add(line);
        }
        validateLines(lines);
        return lines;
    }

    private void validateRequest(JournalEntryRequest request) {
        if (request.lines() == null || request.lines().size() < 2) {
            throw new JournalEntryValidationException("Un assentament ha de tenir almenys 2 linies");
        }
        if (request.description() == null || request.description().isBlank()) {
            throw new JournalEntryValidationException("La descripcio es obligatoria");
        }
    }

    private void validateLines(List<JournalLine> lines) {
        BigDecimal totalDebit = BigDecimal.ZERO;
        BigDecimal totalCredit = BigDecimal.ZERO;

        for (JournalLine line : lines) {
            if (line.getDebit().compareTo(BigDecimal.ZERO) < 0 || line.getCredit().compareTo(BigDecimal.ZERO) < 0) {
                throw new JournalEntryValidationException("El deure i l'haver no poden ser negatius");
            }
            if (line.getDebit().compareTo(BigDecimal.ZERO) > 0 && line.getCredit().compareTo(BigDecimal.ZERO) > 0) {
                throw new JournalEntryValidationException("Una linia no pot tenir deure i haver alhora");
            }
            if (line.getDebit().compareTo(BigDecimal.ZERO) == 0 && line.getCredit().compareTo(BigDecimal.ZERO) == 0) {
                throw new JournalEntryValidationException("Cada linia ha de tenir deure o haver");
            }
            totalDebit = totalDebit.add(line.getDebit());
            totalCredit = totalCredit.add(line.getCredit());
        }

        if (totalDebit.compareTo(totalCredit) != 0) {
            throw new JournalEntryValidationException(
                "L'assentament no esta quadrat: Deure=" + totalDebit + ", Haver=" + totalCredit
            );
        }
    }

    private BigDecimal scale(BigDecimal value) {
        return (value == null ? BigDecimal.ZERO : value).setScale(2, RoundingMode.HALF_UP);
    }

    private String normalizeNullable(String value) {
        return value == null || value.isBlank() ? null : value.trim();
    }
}
