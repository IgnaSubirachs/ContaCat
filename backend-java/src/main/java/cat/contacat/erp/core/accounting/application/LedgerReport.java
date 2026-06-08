package cat.contacat.erp.core.accounting.application;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public record LedgerReport(
    String accountId,
    String accountCode,
    String accountName,
    LocalDate startDate,
    LocalDate endDate,
    BigDecimal finalBalance,
    List<LedgerLineView> lines
) {
}
