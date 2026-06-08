package cat.contacat.erp.core.accounting.application;

import java.math.BigDecimal;

public record ProfitLossAccountLine(
    String code,
    String name,
    BigDecimal amount
) {
}
