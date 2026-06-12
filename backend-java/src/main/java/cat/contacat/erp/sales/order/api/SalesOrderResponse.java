package cat.contacat.erp.sales.order.api;

import cat.contacat.erp.sales.order.SalesOrder;
import cat.contacat.erp.sales.order.SalesOrderLine;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

public record SalesOrderResponse(
    String id,
    String companyId,
    String partnerId,
    String partnerName,
    String quoteId,
    String quoteNumber,
    String series,
    int fiscalYear,
    int sequenceNumber,
    String orderNumber,
    LocalDate orderDate,
    String status,
    LocalDate deliveryDate,
    String deliveryAddress,
    String notes,
    BigDecimal subtotal,
    BigDecimal totalTax,
    BigDecimal total,
    List<SalesOrderLineResponse> lines,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt
) {
    public static SalesOrderResponse from(SalesOrder order) {
        BigDecimal subtotal = order.getLines().stream().map(SalesOrderResponse::lineBase).reduce(BigDecimal.ZERO, BigDecimal::add).setScale(2, RoundingMode.HALF_UP);
        BigDecimal tax = order.getLines().stream().map(SalesOrderResponse::lineTax).reduce(BigDecimal.ZERO, BigDecimal::add).setScale(2, RoundingMode.HALF_UP);
        return new SalesOrderResponse(
            order.getId(),
            order.getCompany().getId(),
            order.getPartner().getId(),
            order.getPartner().getName(),
            order.getQuote() == null ? null : order.getQuote().getId(),
            order.getQuote() == null ? null : order.getQuote().getQuoteNumber(),
            order.getSeries(),
            order.getFiscalYear(),
            order.getSequenceNumber(),
            order.getOrderNumber(),
            order.getOrderDate(),
            order.getStatus().name(),
            order.getDeliveryDate(),
            order.getDeliveryAddress(),
            order.getNotes(),
            subtotal,
            tax,
            subtotal.add(tax).setScale(2, RoundingMode.HALF_UP),
            order.getLines().stream().map(SalesOrderLineResponse::from).toList(),
            order.getCreatedAt(),
            order.getUpdatedAt()
        );
    }

    private static BigDecimal lineBase(SalesOrderLine line) {
        BigDecimal subtotal = line.getQuantity().multiply(line.getUnitPrice());
        BigDecimal discount = subtotal.multiply(line.getDiscountPercent()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
        return subtotal.subtract(discount).setScale(2, RoundingMode.HALF_UP);
    }

    private static BigDecimal lineTax(SalesOrderLine line) {
        BigDecimal base = lineBase(line);
        return base.multiply(line.getTaxRate()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
    }
}
