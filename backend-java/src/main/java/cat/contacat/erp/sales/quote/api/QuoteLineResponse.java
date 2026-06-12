package cat.contacat.erp.sales.quote.api;

import cat.contacat.erp.sales.quote.QuoteLine;
import java.math.BigDecimal;

public record QuoteLineResponse(
    int lineOrder,
    String productCode,
    String description,
    BigDecimal quantity,
    BigDecimal unitPrice,
    BigDecimal discountPercent,
    BigDecimal taxRate,
    BigDecimal subtotal,
    BigDecimal discountAmount,
    BigDecimal taxAmount,
    BigDecimal total
) {

    public static QuoteLineResponse from(QuoteLine line) {
        BigDecimal subtotal = line.getQuantity().multiply(line.getUnitPrice()).setScale(2, java.math.RoundingMode.HALF_UP);
        BigDecimal discountAmount = subtotal.multiply(line.getDiscountPercent()).divide(new BigDecimal("100.00"), 2, java.math.RoundingMode.HALF_UP);
        BigDecimal baseAfterDiscount = subtotal.subtract(discountAmount);
        BigDecimal taxAmount = baseAfterDiscount.multiply(line.getTaxRate()).divide(new BigDecimal("100.00"), 2, java.math.RoundingMode.HALF_UP);
        BigDecimal total = baseAfterDiscount.add(taxAmount);
        return new QuoteLineResponse(
            line.getLineOrder(),
            line.getProductCode(),
            line.getDescription(),
            line.getQuantity(),
            line.getUnitPrice(),
            line.getDiscountPercent(),
            line.getTaxRate(),
            subtotal,
            discountAmount,
            taxAmount,
            total
        );
    }
}
