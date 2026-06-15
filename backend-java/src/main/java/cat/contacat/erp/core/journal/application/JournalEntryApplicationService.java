package cat.contacat.erp.core.journal.application;

import cat.contacat.erp.core.account.Account;
import cat.contacat.erp.core.account.application.AccountApplicationService;
import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.JournalEntryAlreadyPostedException;
import cat.contacat.erp.core.journal.JournalEntryNotFoundException;
import cat.contacat.erp.core.journal.JournalEntryRepository;
import cat.contacat.erp.core.journal.JournalEntryStatus;
import cat.contacat.erp.core.journal.JournalEntryValidationException;
import cat.contacat.erp.core.journal.JournalLine;
import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequence;
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
public class JournalEntryApplicationService {

    private final JournalEntryRepository repository;
    private final CompanyRepository companyRepository;
    private final AccountApplicationService accountApplicationService;
    private final DocumentSequenceService documentSequenceService;

    public JournalEntryApplicationService(
        JournalEntryRepository repository,
        CompanyRepository companyRepository,
        AccountApplicationService accountApplicationService,
        DocumentSequenceService documentSequenceService
    ) {
        this.repository = repository;
        this.companyRepository = companyRepository;
        this.accountApplicationService = accountApplicationService;
        this.documentSequenceService = documentSequenceService;
    }

    @Transactional(readOnly = true)
    public List<JournalEntry> list(String companyId, LocalDate startDate, LocalDate endDate) {
        ensureCompanyExists(companyId);
        return (startDate != null && endDate != null)
            ? repository.findAllByCompanyIdAndEntryDateBetweenOrderByEntryDateDescEntryNumberDesc(companyId, startDate, endDate)
            : repository.findAllByCompanyIdOrderByEntryDateDescEntryNumberDesc(companyId);
    }

    @Transactional(readOnly = true)
    public JournalEntry get(String companyId, String entryId) {
        return findEntry(companyId, entryId);
    }

    @Transactional
    public JournalEntry create(String companyId, JournalEntryCommand command) {
        validateCommand(command);
        Company company = findCompany(companyId);
        DocumentNumber number = documentSequenceService.allocateNext(companyId, "JOURNAL_ENTRY", "A", command.entryDate().getYear());

        JournalEntry entry = new JournalEntry();
        entry.setCompany(company);
        entry.setSequence(buildSequenceReference(number.sequenceId()));
        entry.setEntryNumber(number.number());
        entry.setFormattedNumber(number.formattedNumber());
        entry.setEntryDate(command.entryDate());
        entry.setDescription(command.description().trim());
        entry.setAttachmentPath(normalizeNullable(command.attachmentPath()));
        entry.setStatus(JournalEntryStatus.DRAFT);
        entry.setLines(buildLines(companyId, entry, command.lines()));

        return repository.save(entry);
    }

    @Transactional
    public JournalEntry updateDraft(String companyId, String entryId, JournalEntryCommand command) {
        validateCommand(command);
        JournalEntry entry = findEntry(companyId, entryId);
        if (entry.getStatus() == JournalEntryStatus.POSTED) {
            throw new JournalEntryAlreadyPostedException(entryId);
        }

        entry.setEntryDate(command.entryDate());
        entry.setDescription(command.description().trim());
        entry.setAttachmentPath(normalizeNullable(command.attachmentPath()));
        List<JournalLine> replacementLines = buildLines(companyId, entry, command.lines());
        entry.getLines().clear();
        entry.getLines().addAll(replacementLines);
        return repository.save(entry);
    }

    @Transactional
    public JournalEntry post(String companyId, String entryId) {
        JournalEntry entry = findEntry(companyId, entryId);
        if (entry.getStatus() == JournalEntryStatus.POSTED) {
            throw new JournalEntryAlreadyPostedException(entryId);
        }
        validateLines(entry.getLines());
        entry.setStatus(JournalEntryStatus.POSTED);
        entry.setPostedAt(OffsetDateTime.now());
        return repository.save(entry);
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

    private DocumentSequence buildSequenceReference(String sequenceId) {
        DocumentSequence sequence = new DocumentSequence();
        sequence.setId(sequenceId);
        return sequence;
    }

    private List<JournalLine> buildLines(String companyId, JournalEntry entry, List<JournalLineCommand> commands) {
        List<JournalLine> lines = new ArrayList<>();
        int index = 1;
        for (JournalLineCommand command : commands) {
            Account account = accountApplicationService.findAccountByCode(companyId, command.accountCode());

            JournalLine line = new JournalLine();
            line.setJournalEntry(entry);
            line.setAccount(account);
            line.setLineOrder(index++);
            line.setDebit(scale(command.debit()));
            line.setCredit(scale(command.credit()));
            line.setDescription(command.description() == null ? "" : command.description().trim());
            lines.add(line);
        }
        validateLines(lines);
        return lines;
    }

    private void validateCommand(JournalEntryCommand command) {
        if (command.lines() == null || command.lines().size() < 2) {
            throw new JournalEntryValidationException("Un assentament ha de tenir almenys 2 linies");
        }
        if (command.description() == null || command.description().isBlank()) {
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
