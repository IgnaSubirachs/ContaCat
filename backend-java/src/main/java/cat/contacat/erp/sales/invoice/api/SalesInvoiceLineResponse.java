package cat.contacat.erp.sales.invoice.api;

import cat.contacat.erp.sales.invoice.SalesInvoiceLine;
import java.math.BigDecimal;
import java.math.RoundingMode;

public record SalesInvoiceLineResponse(
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
    public static SalesInvoiceLineResponse from(SalesInvoiceLine line) {
        BigDecimal subtotal = line.getQuantity().multiply(line.getUnitPrice());
        BigDecimal discount = subtotal.multiply(line.getDiscountPercent()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
        BigDecimal base = subtotal.subtract(discount).setScale(2, RoundingMode.HALF_UP);
        BigDecimal tax = base.multiply(line.getTaxRate()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
        return new SalesInvoiceLineResponse(
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
