package cat.contacat.erp.core.journal;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.account.Account;
import cat.contacat.erp.core.account.AccountService;
import cat.contacat.erp.core.account.AccountType;
import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.journal.api.JournalEntryRequest;
import cat.contacat.erp.core.journal.api.JournalEntryResponse;
import cat.contacat.erp.core.journal.api.JournalLineRequest;
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
class JournalEntryServiceTest {

    @Mock
    private JournalEntryRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @Mock
    private AccountService accountService;

    @Mock
    private DocumentSequenceService documentSequenceService;

    @InjectMocks
    private JournalEntryService service;

    @Test
    void createAllocatesSequenceAndPersistsBalancedEntry() {
        Company company = new Company();
        company.setId("company-1");
        Account debitAccount = account("account-430", company, "430000", "Clients", AccountType.ASSET);
        Account creditAccount = account("account-700", company, "700000", "Vendes", AccountType.INCOME);

        JournalEntryRequest request = new JournalEntryRequest(
            LocalDate.of(2026, 6, 8),
            "Factura venda",
            null,
            List.of(
                new JournalLineRequest("430000", new BigDecimal("121.00"), BigDecimal.ZERO, "Client"),
                new JournalLineRequest("700000", BigDecimal.ZERO, new BigDecimal("121.00"), "Venda")
            )
        );

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(documentSequenceService.allocateNext("company-1", "JOURNAL_ENTRY", "A", 2026))
            .thenReturn(new DocumentNumber("sequence-1", "company-1", "JOURNAL_ENTRY", "A", 2026, 5, "JE-2026-00005"));
        when(accountService.findAccountByCode("company-1", "430000")).thenReturn(debitAccount);
        when(accountService.findAccountByCode("company-1", "700000")).thenReturn(creditAccount);
        when(repository.save(any(JournalEntry.class))).thenAnswer(invocation -> {
            JournalEntry entry = invocation.getArgument(0);
            entry.setId("entry-1");
            return entry;
        });

        JournalEntryResponse response = service.create("company-1", request);

        assertThat(response.id()).isEqualTo("entry-1");
        assertThat(response.entryNumber()).isEqualTo(5);
        assertThat(response.formattedNumber()).isEqualTo("JE-2026-00005");
        assertThat(response.status()).isEqualTo(JournalEntryStatus.DRAFT);
        assertThat(response.lines()).hasSize(2);
    }

    @Test
    void createFailsWhenEntryIsNotBalanced() {
        Company company = new Company();
        company.setId("company-1");
        Account debitAccount = account("account-430", company, "430000", "Clients", AccountType.ASSET);
        Account creditAccount = account("account-700", company, "700000", "Vendes", AccountType.INCOME);

        JournalEntryRequest request = new JournalEntryRequest(
            LocalDate.of(2026, 6, 8),
            "Factura venda",
            null,
            List.of(
                new JournalLineRequest("430000", new BigDecimal("100.00"), BigDecimal.ZERO, "Client"),
                new JournalLineRequest("700000", BigDecimal.ZERO, new BigDecimal("121.00"), "Venda")
            )
        );

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(documentSequenceService.allocateNext("company-1", "JOURNAL_ENTRY", "A", 2026))
            .thenReturn(new DocumentNumber("sequence-1", "company-1", "JOURNAL_ENTRY", "A", 2026, 5, "JE-2026-00005"));
        when(accountService.findAccountByCode("company-1", "430000")).thenReturn(debitAccount);
        when(accountService.findAccountByCode("company-1", "700000")).thenReturn(creditAccount);

        assertThatThrownBy(() -> service.create("company-1", request))
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

        JournalEntryResponse response = service.post("company-1", "entry-1");

        assertThat(response.status()).isEqualTo(JournalEntryStatus.POSTED);
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
