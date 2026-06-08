package cat.contacat.erp.core.accounting.application;

import java.math.BigDecimal;
import java.time.LocalDate;

public record BalanceSheetReport(
    LocalDate endDate,
    BalanceSheetSection nonCurrentAssets,
    BalanceSheetSection currentAssets,
    BalanceSheetSection equity,
    BalanceSheetSection nonCurrentLiabilities,
    BalanceSheetSection currentLiabilities,
    BigDecimal totalAssets,
    BigDecimal totalEquityAndLiabilities
) {
}
