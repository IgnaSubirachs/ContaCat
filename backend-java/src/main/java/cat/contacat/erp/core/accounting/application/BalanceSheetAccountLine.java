package cat.contacat.erp.core.accounting.application;

import java.math.BigDecimal;

public record BalanceSheetAccountLine(
    String code,
    String name,
    BigDecimal balance
) {
}
