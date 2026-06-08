package cat.contacat.erp.core.accounting.application;

import cat.contacat.erp.core.account.Account;
import cat.contacat.erp.core.account.AccountType;
import cat.contacat.erp.core.account.application.AccountApplicationService;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.JournalEntryRepository;
import cat.contacat.erp.core.journal.JournalEntryStatus;
import cat.contacat.erp.core.journal.JournalLine;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AccountingReportApplicationService {

    private final CompanyRepository companyRepository;
    private final AccountApplicationService accountApplicationService;
    private final JournalEntryRepository journalEntryRepository;

    public AccountingReportApplicationService(
        CompanyRepository companyRepository,
        AccountApplicationService accountApplicationService,
        JournalEntryRepository journalEntryRepository
    ) {
        this.companyRepository = companyRepository;
        this.accountApplicationService = accountApplicationService;
        this.journalEntryRepository = journalEntryRepository;
    }

    @Transactional(readOnly = true)
    public TrialBalanceReport trialBalance(String companyId, LocalDate endDate) {
        ensureCompanyExists(companyId);
        List<Account> accounts = accountApplicationService.list(companyId, null);
        List<TrialBalanceLine> lines = accounts.stream()
            .map(account -> new TrialBalanceLine(
                account.getId(),
                account.getCode(),
                account.getName(),
                account.getAccountType(),
                accountBalance(account, postedEntries(companyId, null, endDate))
            ))
            .filter(line -> line.balance().compareTo(BigDecimal.ZERO) != 0)
            .sorted(Comparator.comparing(TrialBalanceLine::accountCode))
            .toList();
        return new TrialBalanceReport(endDate, lines);
    }

    @Transactional(readOnly = true)
    public LedgerReport ledger(String companyId, String accountCode, LocalDate startDate, LocalDate endDate) {
        ensureCompanyExists(companyId);
        Account account = accountApplicationService.findAccountByCode(companyId, accountCode);
        List<JournalEntry> entries = postedEntries(companyId, startDate, endDate);
        List<LedgerLineView> lines = new ArrayList<>();
        BigDecimal runningBalance = BigDecimal.ZERO;

        for (JournalEntry entry : entries) {
            for (JournalLine line : entry.getLines()) {
                if (!line.getAccount().getId().equals(account.getId())) {
                    continue;
                }
                runningBalance = runningBalance.add(signedAmount(account, line));
                lines.add(new LedgerLineView(
                    entry.getId(),
                    entry.getEntryNumber(),
                    entry.getFormattedNumber(),
                    entry.getEntryDate(),
                    entry.getDescription(),
                    line.getDescription(),
                    line.getDebit(),
                    line.getCredit(),
                    runningBalance
                ));
            }
        }

        return new LedgerReport(
            account.getId(),
            account.getCode(),
            account.getName(),
            startDate,
            endDate,
            runningBalance,
            lines
        );
    }

    @Transactional(readOnly = true)
    public BalanceSheetReport balanceSheet(String companyId, LocalDate endDate) {
        ensureCompanyExists(companyId);
        List<Account> accounts = accountApplicationService.list(companyId, null);
        List<JournalEntry> entries = postedEntries(companyId, null, endDate);

        Map<String, List<BalanceSheetAccountLine>> nonCurrentAssets = new LinkedHashMap<>();
        Map<String, List<BalanceSheetAccountLine>> currentAssets = new LinkedHashMap<>();
        Map<String, List<BalanceSheetAccountLine>> equity = new LinkedHashMap<>();
        Map<String, List<BalanceSheetAccountLine>> nonCurrentLiabilities = new LinkedHashMap<>();
        Map<String, List<BalanceSheetAccountLine>> currentLiabilities = new LinkedHashMap<>();

        for (Account account : accounts) {
            if (!(account.getAccountType() == AccountType.ASSET
                || account.getAccountType() == AccountType.EQUITY
                || account.getAccountType() == AccountType.LIABILITY)) {
                continue;
            }

            BigDecimal balance = accountBalance(account, entries);
            if (balance.compareTo(BigDecimal.ZERO) == 0) {
                continue;
            }

            BalanceSheetAccountLine line = new BalanceSheetAccountLine(account.getCode(), account.getName(), balance);
            addBalanceSheetLine(account, line, nonCurrentAssets, currentAssets, equity, nonCurrentLiabilities, currentLiabilities);
        }

        BigDecimal currentYearResult = profitLoss(companyId, fiscalYearStart(endDate), endDate).resultForYear();
        if (currentYearResult.compareTo(BigDecimal.ZERO) != 0) {
            addGrouped(
                equity,
                "A-1) Fons Propis",
                new BalanceSheetAccountLine("129000", "Resultat de l'exercici", currentYearResult)
            );
        }

        BalanceSheetSection nonCurrentAssetsSection = toBalanceSheetSection(nonCurrentAssets);
        BalanceSheetSection currentAssetsSection = toBalanceSheetSection(currentAssets);
        BalanceSheetSection equitySection = toBalanceSheetSection(equity);
        BalanceSheetSection nonCurrentLiabilitiesSection = toBalanceSheetSection(nonCurrentLiabilities);
        BalanceSheetSection currentLiabilitiesSection = toBalanceSheetSection(currentLiabilities);

        BigDecimal totalAssets = nonCurrentAssetsSection.total().add(currentAssetsSection.total());
        BigDecimal totalEquityAndLiabilities = equitySection.total()
            .add(nonCurrentLiabilitiesSection.total())
            .add(currentLiabilitiesSection.total());

        return new BalanceSheetReport(
            endDate,
            nonCurrentAssetsSection,
            currentAssetsSection,
            equitySection,
            nonCurrentLiabilitiesSection,
            currentLiabilitiesSection,
            totalAssets,
            totalEquityAndLiabilities
        );
    }

    @Transactional(readOnly = true)
    public ProfitLossReport profitLoss(String companyId, LocalDate startDate, LocalDate endDate) {
        ensureCompanyExists(companyId);
        List<Account> accounts = accountApplicationService.list(companyId, null);
        List<JournalEntry> entries = postedEntries(companyId, startDate, endDate);

        Map<String, List<ProfitLossAccountLine>> groups = new LinkedHashMap<>();
        BigDecimal operatingResult = BigDecimal.ZERO;
        BigDecimal financialResult = BigDecimal.ZERO;
        BigDecimal taxes = BigDecimal.ZERO;

        for (Account account : accounts) {
            if (!(account.getAccountType() == AccountType.INCOME || account.getAccountType() == AccountType.EXPENSE)) {
                continue;
            }

            BigDecimal amount = accountBalance(account, entries);
            if (amount.compareTo(BigDecimal.ZERO) == 0) {
                continue;
            }

            String groupName;
            if (account.getAccountType() == AccountType.INCOME) {
                groupName = incomeGroup(account.getCode());
                operatingResult = operatingResult.add(isFinancialIncome(account.getCode()) ? BigDecimal.ZERO : amount);
                financialResult = financialResult.add(isFinancialIncome(account.getCode()) ? amount : BigDecimal.ZERO);
            } else {
                BigDecimal signedExpense = amount.negate();
                groupName = expenseGroup(account.getCode());
                if (account.getCode().startsWith("63")) {
                    taxes = taxes.add(signedExpense);
                } else if (account.getCode().startsWith("66")) {
                    financialResult = financialResult.add(signedExpense);
                } else {
                    operatingResult = operatingResult.add(signedExpense);
                }
                amount = signedExpense;
            }

            groups.computeIfAbsent(groupName, ignored -> new ArrayList<>())
                .add(new ProfitLossAccountLine(account.getCode(), account.getName(), amount));
        }

        List<ProfitLossGroup> resultGroups = groups.entrySet().stream()
            .map(entry -> new ProfitLossGroup(
                entry.getKey(),
                entry.getValue().stream().map(ProfitLossAccountLine::amount).reduce(BigDecimal.ZERO, BigDecimal::add),
                entry.getValue()
            ))
            .toList();

        BigDecimal resultBeforeTax = operatingResult.add(financialResult);
        BigDecimal resultForYear = resultBeforeTax.add(taxes);

        return new ProfitLossReport(startDate, endDate, resultGroups, operatingResult, financialResult, resultBeforeTax, resultForYear);
    }

    private void ensureCompanyExists(String companyId) {
        if (!companyRepository.existsById(companyId)) {
            throw new CompanyNotFoundException(companyId);
        }
    }

    private List<JournalEntry> postedEntries(String companyId, LocalDate startDate, LocalDate endDate) {
        return journalEntryRepository.findAllByCompanyIdOrderByEntryDateAscEntryNumberAsc(companyId).stream()
            .filter(entry -> entry.getStatus() == JournalEntryStatus.POSTED)
            .filter(entry -> startDate == null || !entry.getEntryDate().isBefore(startDate))
            .filter(entry -> endDate == null || !entry.getEntryDate().isAfter(endDate))
            .toList();
    }

    private LocalDate fiscalYearStart(LocalDate endDate) {
        LocalDate effectiveEndDate = endDate != null ? endDate : LocalDate.now();
        return LocalDate.of(effectiveEndDate.getYear(), 1, 1);
    }

    private BigDecimal accountBalance(Account account, List<JournalEntry> entries) {
        BigDecimal debit = BigDecimal.ZERO;
        BigDecimal credit = BigDecimal.ZERO;

        for (JournalEntry entry : entries) {
            for (JournalLine line : entry.getLines()) {
                if (!line.getAccount().getId().equals(account.getId())) {
                    continue;
                }
                debit = debit.add(line.getDebit());
                credit = credit.add(line.getCredit());
            }
        }

        return account.getAccountType().isDebitNature()
            ? debit.subtract(credit)
            : credit.subtract(debit);
    }

    private BigDecimal signedAmount(Account account, JournalLine line) {
        return account.getAccountType().isDebitNature()
            ? line.getDebit().subtract(line.getCredit())
            : line.getCredit().subtract(line.getDebit());
    }

    private void addBalanceSheetLine(
        Account account,
        BalanceSheetAccountLine line,
        Map<String, List<BalanceSheetAccountLine>> nonCurrentAssets,
        Map<String, List<BalanceSheetAccountLine>> currentAssets,
        Map<String, List<BalanceSheetAccountLine>> equity,
        Map<String, List<BalanceSheetAccountLine>> nonCurrentLiabilities,
        Map<String, List<BalanceSheetAccountLine>> currentLiabilities
    ) {
        String code = account.getCode();
        if (account.getAccountType() == AccountType.ASSET) {
            if (code.startsWith("2")) {
                addGrouped(nonCurrentAssets, nonCurrentAssetGroup(code), line);
            } else {
                addGrouped(currentAssets, currentAssetGroup(code), line);
            }
            return;
        }

        if (account.getAccountType() == AccountType.EQUITY) {
            addGrouped(equity, "A-1) Fons Propis", line);
            return;
        }

        if (code.startsWith("13") || code.startsWith("14") || code.startsWith("15") || code.startsWith("16") || code.startsWith("17")) {
            addGrouped(nonCurrentLiabilities, "II. Deutes a llarg termini", line);
        } else if (code.startsWith("40") || code.startsWith("41")) {
            addGrouped(currentLiabilities, "IV. Creditors comercials i altres comptes a pagar", line);
        } else if (code.startsWith("52")) {
            addGrouped(currentLiabilities, "III. Deutes a curt termini", line);
        } else {
            addGrouped(currentLiabilities, "V. Altres passius corrents", line);
        }
    }

    private String nonCurrentAssetGroup(String code) {
        if (code.startsWith("20")) return "I. Immobilitzat Intangible";
        if (code.startsWith("21")) return "II. Immobilitzat Material";
        if (code.startsWith("22")) return "III. Inversions Immobiliaries";
        if (code.startsWith("25") || code.startsWith("26")) return "V. Inversions financeres a llarg termini";
        return "VI. Altres actius no corrents";
    }

    private String currentAssetGroup(String code) {
        if (code.startsWith("3")) return "I. Existencies";
        if (code.startsWith("43") || code.startsWith("44")) return "II. Deutors comercials i altres comptes a cobrar";
        if (code.startsWith("57")) return "VII. Efectiu i altres actius liquids equivalents";
        return "VI. Altres actius corrents";
    }

    private String incomeGroup(String code) {
        if (code.startsWith("70")) return "1. Import net de la xifra de negocis";
        if (code.startsWith("74")) return "3. Subvencions d'explotacio";
        if (code.startsWith("76")) return "12. Ingressos financers";
        return "5. Altres ingressos d'explotacio";
    }

    private String expenseGroup(String code) {
        if (code.startsWith("60")) return "4. Aprovisionaments";
        if (code.startsWith("64")) return "6. Despeses de personal";
        if (code.startsWith("62")) return "7. Altres despeses d'explotacio";
        if (code.startsWith("68")) return "8. Amortitzacio de l'immobilitzat";
        if (code.startsWith("66")) return "13. Despeses financeres";
        if (code.startsWith("63")) return "16. Impostos sobre beneficis";
        return "7. Altres despeses d'explotacio";
    }

    private boolean isFinancialIncome(String code) {
        return code.startsWith("76");
    }

    private void addGrouped(Map<String, List<BalanceSheetAccountLine>> target, String group, BalanceSheetAccountLine line) {
        target.computeIfAbsent(group, ignored -> new ArrayList<>()).add(line);
    }

    private BalanceSheetSection toBalanceSheetSection(Map<String, List<BalanceSheetAccountLine>> source) {
        List<BalanceSheetGroup> groups = source.entrySet().stream()
            .map(entry -> new BalanceSheetGroup(
                entry.getKey(),
                entry.getValue().stream().map(BalanceSheetAccountLine::balance).reduce(BigDecimal.ZERO, BigDecimal::add),
                entry.getValue()
            ))
            .toList();

        BigDecimal total = groups.stream().map(BalanceSheetGroup::total).reduce(BigDecimal.ZERO, BigDecimal::add);
        return new BalanceSheetSection(total, groups);
    }
}
