package cat.contacat.erp.core.accounting.api;

import cat.contacat.erp.core.accounting.application.AccountingReportApplicationService;
import cat.contacat.erp.core.accounting.application.BalanceSheetReport;
import cat.contacat.erp.core.accounting.application.LedgerReport;
import cat.contacat.erp.core.accounting.application.ProfitLossReport;
import cat.contacat.erp.core.accounting.application.TrialBalanceReport;
import java.time.LocalDate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/core/companies/{companyId}/accounting/reports")
public class AccountingReportController {

    private final AccountingReportApplicationService service;

    public AccountingReportController(AccountingReportApplicationService service) {
        this.service = service;
    }

    @GetMapping("/trial-balance")
    public TrialBalanceReport trialBalance(@PathVariable String companyId, @RequestParam(required = false) LocalDate endDate) {
        return service.trialBalance(companyId, endDate);
    }

    @GetMapping("/ledger/{accountCode}")
    public LedgerReport ledger(
        @PathVariable String companyId,
        @PathVariable String accountCode,
        @RequestParam(required = false) LocalDate startDate,
        @RequestParam(required = false) LocalDate endDate
    ) {
        return service.ledger(companyId, accountCode, startDate, endDate);
    }

    @GetMapping("/balance-sheet")
    public BalanceSheetReport balanceSheet(@PathVariable String companyId, @RequestParam(required = false) LocalDate endDate) {
        return service.balanceSheet(companyId, endDate);
    }

    @GetMapping("/profit-loss")
    public ProfitLossReport profitLoss(
        @PathVariable String companyId,
        @RequestParam(required = false) LocalDate startDate,
        @RequestParam(required = false) LocalDate endDate
    ) {
        return service.profitLoss(companyId, startDate, endDate);
    }
}
