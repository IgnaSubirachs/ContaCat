package cat.contacat.erp.sales.quote.api;

import cat.contacat.erp.sales.quote.Quote;
import cat.contacat.erp.sales.quote.QuoteLine;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.OffsetDateTime;
import java.util.List;

public record QuoteResponse(
    String id,
    String companyId,
    String partnerId,
    String partnerName,
    String series,
    int fiscalYear,
    int sequenceNumber,
    String quoteNumber,
    java.time.LocalDate quoteDate,
    java.time.LocalDate validUntil,
    String status,
    String notes,
    BigDecimal subtotal,
    BigDecimal totalTax,
    BigDecimal total,
    List<QuoteLineResponse> lines,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt
) {

    public static QuoteResponse from(Quote quote) {
        BigDecimal subtotal = quote.getLines().stream()
            .map(QuoteResponse::lineBaseAfterDiscount)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
            .setScale(2, RoundingMode.HALF_UP);
        BigDecimal totalTax = quote.getLines().stream()
            .map(QuoteResponse::lineTax)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
            .setScale(2, RoundingMode.HALF_UP);
        return new QuoteResponse(
            quote.getId(),
            quote.getCompany().getId(),
            quote.getPartner().getId(),
            quote.getPartner().getName(),
            quote.getSeries(),
            quote.getFiscalYear(),
            quote.getSequenceNumber(),
            quote.getQuoteNumber(),
            quote.getQuoteDate(),
            quote.getValidUntil(),
            quote.getStatus().name(),
            quote.getNotes(),
            subtotal,
            totalTax,
            subtotal.add(totalTax).setScale(2, RoundingMode.HALF_UP),
            quote.getLines().stream().map(QuoteLineResponse::from).toList(),
            quote.getCreatedAt(),
            quote.getUpdatedAt()
        );
    }

    private static BigDecimal lineBaseAfterDiscount(QuoteLine line) {
        BigDecimal subtotal = line.getQuantity().multiply(line.getUnitPrice());
        BigDecimal discount = subtotal.multiply(line.getDiscountPercent()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
        return subtotal.subtract(discount).setScale(2, RoundingMode.HALF_UP);
    }

    private static BigDecimal lineTax(QuoteLine line) {
        BigDecimal base = lineBaseAfterDiscount(line);
        return base.multiply(line.getTaxRate()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
    }
}
