package cat.contacat.erp.sales.quote.application;

import java.math.BigDecimal;

public record QuoteLineCommand(
    String productCode,
    String description,
    BigDecimal quantity,
    BigDecimal unitPrice,
    BigDecimal discountPercent,
    BigDecimal taxRate
) {
}
