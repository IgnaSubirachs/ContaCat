package cat.contacat.erp.sales.order.application;

import java.math.BigDecimal;

public record SalesOrderLineCommand(
    String productCode,
    String description,
    BigDecimal quantity,
    BigDecimal unitPrice,
    BigDecimal discountPercent,
    BigDecimal taxRate
) {
}
