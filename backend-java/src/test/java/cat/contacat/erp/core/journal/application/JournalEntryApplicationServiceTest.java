package cat.contacat.erp.core.journal.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.account.Account;
import cat.contacat.erp.core.account.AccountType;
import cat.contacat.erp.core.account.application.AccountApplicationService;
import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.JournalEntryAlreadyPostedException;
import cat.contacat.erp.core.journal.JournalEntryRepository;
import cat.contacat.erp.core.journal.JournalEntryStatus;
import cat.contacat.erp.core.journal.JournalEntryValidationException;
import cat.contacat.erp.core.journal.JournalLine;
import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequenceService;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class JournalEntryApplicationServiceTest {

    @Mock
    private JournalEntryRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @Mock
    private AccountApplicationService accountApplicationService;

    @Mock
    private DocumentSequenceService documentSequenceService;

    @InjectMocks
    private JournalEntryApplicationService service;

    @Test
    void createAllocatesSequenceAndPersistsBalancedEntry() {
        Company company = new Company();
        company.setId("company-1");
        Account debitAccount = account("account-430", company, "430000", "Clients", AccountType.ASSET);
        Account creditAccount = account("account-700", company, "700000", "Vendes", AccountType.INCOME);

        JournalEntryCommand command = new JournalEntryCommand(
            LocalDate.of(2026, 6, 8),
            "Factura venda",
            null,
            List.of(
                new JournalLineCommand("430000", new BigDecimal("121.00"), BigDecimal.ZERO, "Client"),
                new JournalLineCommand("700000", BigDecimal.ZERO, new BigDecimal("121.00"), "Venda")
            )
        );

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(documentSequenceService.allocateNext("company-1", "JOURNAL_ENTRY", "A", 2026))
            .thenReturn(new DocumentNumber("sequence-1", "company-1", "JOURNAL_ENTRY", "A", 2026, 5, "JE-2026-00005"));
        when(accountApplicationService.findAccountByCode("company-1", "430000")).thenReturn(debitAccount);
        when(accountApplicationService.findAccountByCode("company-1", "700000")).thenReturn(creditAccount);
        when(repository.save(any(JournalEntry.class))).thenAnswer(invocation -> {
            JournalEntry entry = invocation.getArgument(0);
            entry.setId("entry-1");
            return entry;
        });

        JournalEntry entry = service.create("company-1", command);

        assertThat(entry.getId()).isEqualTo("entry-1");
        assertThat(entry.getEntryNumber()).isEqualTo(5);
        assertThat(entry.getFormattedNumber()).isEqualTo("JE-2026-00005");
        assertThat(entry.getStatus()).isEqualTo(JournalEntryStatus.DRAFT);
        assertThat(entry.getLines()).hasSize(2);
    }

    @Test
    void createFailsWhenEntryIsNotBalanced() {
        Company company = new Company();
        company.setId("company-1");
        Account debitAccount = account("account-430", company, "430000", "Clients", AccountType.ASSET);
        Account creditAccount = account("account-700", company, "700000", "Vendes", AccountType.INCOME);

        JournalEntryCommand command = new JournalEntryCommand(
            LocalDate.of(2026, 6, 8),
            "Factura venda",
            null,
            List.of(
                new JournalLineCommand("430000", new BigDecimal("100.00"), BigDecimal.ZERO, "Client"),
                new JournalLineCommand("700000", BigDecimal.ZERO, new BigDecimal("121.00"), "Venda")
            )
        );

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(documentSequenceService.allocateNext("company-1", "JOURNAL_ENTRY", "A", 2026))
            .thenReturn(new DocumentNumber("sequence-1", "company-1", "JOURNAL_ENTRY", "A", 2026, 5, "JE-2026-00005"));
        when(accountApplicationService.findAccountByCode("company-1", "430000")).thenReturn(debitAccount);
        when(accountApplicationService.findAccountByCode("company-1", "700000")).thenReturn(creditAccount);

        assertThatThrownBy(() -> service.create("company-1", command))
            .isInstanceOf(JournalEntryValidationException.class)
            .hasMessageContaining("no esta quadrat");
    }

    @Test
    void postMarksEntryAsPosted() {
        Company company = new Company();
        company.setId("company-1");
        JournalEntry entry = new JournalEntry();
        entry.setId("entry-1");
        entry.setCompany(company);
        entry.setStatus(JournalEntryStatus.DRAFT);
        entry.setLines(List.of(
            line(account("a1", company, "430000", "Clients", AccountType.ASSET), 1, new BigDecimal("10.00"), BigDecimal.ZERO),
            line(account("a2", company, "700000", "Vendes", AccountType.INCOME), 2, BigDecimal.ZERO, new BigDecimal("10.00"))
        ));

        when(repository.findById("entry-1")).thenReturn(Optional.of(entry));
        when(repository.save(entry)).thenReturn(entry);

        JournalEntry response = service.post("company-1", "entry-1");

        assertThat(response.getStatus()).isEqualTo(JournalEntryStatus.POSTED);
        assertThat(entry.getPostedAt()).isNotNull();
        verify(repository).save(entry);
    }

    @Test
    void postFailsWhenAlreadyPosted() {
        Company company = new Company();
        company.setId("company-1");
        JournalEntry entry = new JournalEntry();
        entry.setId("entry-1");
        entry.setCompany(company);
        entry.setStatus(JournalEntryStatus.POSTED);

        when(repository.findById("entry-1")).thenReturn(Optional.of(entry));

        assertThatThrownBy(() -> service.post("company-1", "entry-1"))
            .isInstanceOf(JournalEntryAlreadyPostedException.class);
    }

    @Test
    void updateDraftReplacesEditableDataWithoutChangingNumber() {
        Company company = new Company();
        company.setId("company-1");
        JournalEntry entry = new JournalEntry();
        entry.setId("entry-1");
        entry.setCompany(company);
        entry.setEntryNumber(5);
        entry.setFormattedNumber("JE-2026-00005");
        entry.setStatus(JournalEntryStatus.DRAFT);
        entry.setLines(new java.util.ArrayList<>());
        JournalEntryCommand command = new JournalEntryCommand(
            LocalDate.of(2026, 6, 15),
            "Factura corregida",
            "factura.pdf",
            List.of(
                new JournalLineCommand("600000", new BigDecimal("100.00"), BigDecimal.ZERO, "Compra"),
                new JournalLineCommand("400000", BigDecimal.ZERO, new BigDecimal("100.00"), "Proveidor")
            )
        );
        when(repository.findById("entry-1")).thenReturn(Optional.of(entry));
        when(accountApplicationService.findAccountByCode("company-1", "600000"))
            .thenReturn(account("a1", company, "600000", "Compres", AccountType.EXPENSE));
        when(accountApplicationService.findAccountByCode("company-1", "400000"))
            .thenReturn(account("a2", company, "400000", "Proveidors", AccountType.LIABILITY));
        when(repository.save(entry)).thenReturn(entry);

        JournalEntry updated = service.updateDraft("company-1", "entry-1", command);

        assertThat(updated.getFormattedNumber()).isEqualTo("JE-2026-00005");
        assertThat(updated.getDescription()).isEqualTo("Factura corregida");
        assertThat(updated.getLines()).hasSize(2);
    }

    @Test
    void updateDraftRejectsPostedEntries() {
        Company company = new Company();
        company.setId("company-1");
        JournalEntry entry = new JournalEntry();
        entry.setId("entry-1");
        entry.setCompany(company);
        entry.setStatus(JournalEntryStatus.POSTED);
        when(repository.findById("entry-1")).thenReturn(Optional.of(entry));

        assertThatThrownBy(() -> service.updateDraft("company-1", "entry-1", new JournalEntryCommand(
            LocalDate.now(),
            "Intent de canvi",
            null,
            List.of(
                new JournalLineCommand("600000", BigDecimal.ONE, BigDecimal.ZERO, ""),
                new JournalLineCommand("400000", BigDecimal.ZERO, BigDecimal.ONE, "")
            )
        ))).isInstanceOf(JournalEntryAlreadyPostedException.class);
    }

    private Account account(String id, Company company, String code, String name, AccountType type) {
        Account account = new Account();
        account.setId(id);
        account.setCompany(company);
        account.setCode(code);
        account.setName(name);
        account.setAccountType(type);
        account.setGroup(Integer.parseInt(code.substring(0, 1)));
        return account;
    }

    private JournalLine line(Account account, int order, BigDecimal debit, BigDecimal credit) {
        JournalLine line = new JournalLine();
        line.setAccount(account);
        line.setLineOrder(order);
        line.setDebit(debit);
        line.setCredit(credit);
        line.setDescription("");
        return line;
    }
}
