package cat.contacat.erp.core.accounting.application;

import java.time.LocalDate;
import java.util.List;

public record TrialBalanceReport(
    LocalDate endDate,
    List<TrialBalanceLine> lines
) {
}
