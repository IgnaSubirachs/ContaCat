package cat.contacat.erp.sales.order.api;

import cat.contacat.erp.sales.order.SalesOrderLine;
import java.math.BigDecimal;
import java.math.RoundingMode;

public record SalesOrderLineResponse(
    int lineOrder,
    String productCode,
    String description,
    BigDecimal quantity,
    BigDecimal unitPrice,
    BigDecimal discountPercent,
    BigDecimal taxRate,
    BigDecimal subtotal,
    BigDecimal taxAmount,
    BigDecimal total
) {
    public static SalesOrderLineResponse from(SalesOrderLine line) {
        BigDecimal subtotal = line.getQuantity().multiply(line.getUnitPrice()).setScale(2, RoundingMode.HALF_UP);
        BigDecimal discount = subtotal.multiply(line.getDiscountPercent()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
        BigDecimal base = subtotal.subtract(discount).setScale(2, RoundingMode.HALF_UP);
        BigDecimal tax = base.multiply(line.getTaxRate()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
        return new SalesOrderLineResponse(
            line.getLineOrder(),
            line.getProductCode(),
            line.getDescription(),
            line.getQuantity(),
            line.getUnitPrice(),
            line.getDiscountPercent(),
            line.getTaxRate(),
            base,
            tax,
            base.add(tax).setScale(2, RoundingMode.HALF_UP)
        );
    }
}
