package cat.contacat.erp.integration;

import static org.assertj.core.api.Assertions.assertThat;

import cat.contacat.erp.core.account.AccountType;
import cat.contacat.erp.core.account.application.AccountApplicationService;
import cat.contacat.erp.core.account.application.AccountCommand;
import cat.contacat.erp.core.accounting.application.AccountingReportApplicationService;
import cat.contacat.erp.core.accounting.application.BalanceSheetReport;
import cat.contacat.erp.core.accounting.application.LedgerReport;
import cat.contacat.erp.core.accounting.application.ProfitLossReport;
import cat.contacat.erp.core.accounting.application.TrialBalanceReport;
import cat.contacat.erp.core.company.application.CompanyApplicationService;
import cat.contacat.erp.core.company.application.CompanyCommand;
import cat.contacat.erp.core.journal.application.JournalEntryApplicationService;
import cat.contacat.erp.core.journal.application.JournalEntryCommand;
import cat.contacat.erp.core.journal.application.JournalLineCommand;
import cat.contacat.erp.core.sequence.DocumentSequence;
import cat.contacat.erp.core.sequence.DocumentSequenceRepository;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.testcontainers.junit.jupiter.Testcontainers;

@SpringBootTest
@Testcontainers(disabledWithoutDocker = true)
class AccountingReportsIntegrationTest extends AbstractMySqlIntegrationTest {

    @Autowired
    private CompanyApplicationService companyService;

    @Autowired
    private AccountApplicationService accountService;

    @Autowired
    private JournalEntryApplicationService journalService;

    @Autowired
    private AccountingReportApplicationService reportService;

    @Autowired
    private DocumentSequenceRepository documentSequenceRepository;

    private String companyId;

    @BeforeEach
    void setUpCompanyAndAccounts() {
        companyId = companyService.create(new CompanyCommand("ERP Reports", "ERP Reports SL", "B55555555", "ES", "EUR", true)).getId();
        seedJournalEntrySequence(companyId, 2026);

        accountService.create(companyId, new AccountCommand("100000", "Capital social", AccountType.EQUITY, 1, null, true));
        accountService.create(companyId, new AccountCommand("430000", "Clients", AccountType.ASSET, 4, null, true));
        accountService.create(companyId, new AccountCommand("477000", "IVA repercutit", AccountType.LIABILITY, 4, null, true));
        accountService.create(companyId, new AccountCommand("572000", "Bancs", AccountType.ASSET, 5, null, true));
        accountService.create(companyId, new AccountCommand("700000", "Vendes", AccountType.INCOME, 7, null, true));
    }

    @Test
    void reportsReflectPostedEntriesAgainstRealMysqlSchema() {
        journalService.post(companyId, journalService.create(companyId, new JournalEntryCommand(
            LocalDate.of(2026, 1, 1),
            "Aportacio inicial",
            null,
            List.of(
                new JournalLineCommand("572000", new BigDecimal("1000.00"), BigDecimal.ZERO, "Banc"),
                new JournalLineCommand("100000", BigDecimal.ZERO, new BigDecimal("1000.00"), "Capital")
            )
        )).getId());

        journalService.post(companyId, journalService.create(companyId, new JournalEntryCommand(
            LocalDate.of(2026, 1, 15),
            "Factura venda",
            null,
            List.of(
                new JournalLineCommand("430000", new BigDecimal("121.00"), BigDecimal.ZERO, "Client"),
                new JournalLineCommand("700000", BigDecimal.ZERO, new BigDecimal("100.00"), "Venda"),
                new JournalLineCommand("477000", BigDecimal.ZERO, new BigDecimal("21.00"), "IVA")
            )
        )).getId());

        TrialBalanceReport trialBalance = reportService.trialBalance(companyId, LocalDate.of(2026, 12, 31));
        LedgerReport ledger = reportService.ledger(companyId, "430000", null, LocalDate.of(2026, 12, 31));
        BalanceSheetReport balanceSheet = reportService.balanceSheet(companyId, LocalDate.of(2026, 12, 31));
        ProfitLossReport profitLoss = reportService.profitLoss(companyId, LocalDate.of(2026, 1, 1), LocalDate.of(2026, 12, 31));

        assertThat(trialBalance.lines()).extracting("accountCode")
            .contains("100000", "430000", "477000", "572000", "700000");

        assertThat(ledger.lines()).hasSize(1);
        assertThat(ledger.finalBalance()).isEqualByComparingTo("121.00");

        assertThat(balanceSheet.totalAssets()).isEqualByComparingTo("1121.00");
        assertThat(balanceSheet.totalEquityAndLiabilities()).isEqualByComparingTo("1121.00");
        assertThat(balanceSheet.currentAssets().groups()).anyMatch(group -> group.accounts().stream().anyMatch(line -> line.code().equals("430000")));

        assertThat(profitLoss.operatingResult()).isEqualByComparingTo("100.00");
        assertThat(profitLoss.resultForYear()).isEqualByComparingTo("100.00");
        assertThat(profitLoss.groups()).anyMatch(group -> group.name().equals("1. Import net de la xifra de negocis"));
    }

    private void seedJournalEntrySequence(String companyId, int fiscalYear) {
        DocumentSequence sequence = new DocumentSequence();
        sequence.setCompany(companyService.get(companyId));
        sequence.setDocumentType("JOURNAL_ENTRY");
        sequence.setSeries("A");
        sequence.setFiscalYear(fiscalYear);
        sequence.setPrefix("JE-" + fiscalYear + "-");
        sequence.setNextNumber(1);
        sequence.setPadding(5);
        sequence.setActive(true);
        documentSequenceRepository.save(sequence);
    }
}
