package cat.contacat.erp.sales.invoice.api;

import cat.contacat.erp.sales.invoice.SalesInvoice;
import cat.contacat.erp.sales.invoice.SalesInvoiceLine;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

public record SalesInvoiceResponse(
    String id,
    String companyId,
    String partnerId,
    String partnerName,
    String salesOrderId,
    String salesOrderNumber,
    String journalEntryId,
    String journalEntryNumber,
    String invoiceNumber,
    LocalDate invoiceDate,
    LocalDate dueDate,
    String status,
    String notes,
    BigDecimal subtotal,
    BigDecimal totalTax,
    BigDecimal total,
    List<SalesInvoiceLineResponse> lines,
    OffsetDateTime issuedAt,
    OffsetDateTime paidAt,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt
) {
    public static SalesInvoiceResponse from(SalesInvoice invoice) {
        BigDecimal subtotal = invoice.getLines().stream().map(SalesInvoiceResponse::lineBase).reduce(BigDecimal.ZERO, BigDecimal::add).setScale(2, RoundingMode.HALF_UP);
        BigDecimal tax = invoice.getLines().stream().map(SalesInvoiceResponse::lineTax).reduce(BigDecimal.ZERO, BigDecimal::add).setScale(2, RoundingMode.HALF_UP);
        return new SalesInvoiceResponse(
            invoice.getId(),
            invoice.getCompany().getId(),
            invoice.getPartner().getId(),
            invoice.getPartner().getName(),
            invoice.getSalesOrder().getId(),
            invoice.getSalesOrder().getOrderNumber(),
            invoice.getJournalEntry() == null ? null : invoice.getJournalEntry().getId(),
            invoice.getJournalEntry() == null ? null : invoice.getJournalEntry().getFormattedNumber(),
            invoice.getInvoiceNumber(),
            invoice.getInvoiceDate(),
            invoice.getDueDate(),
            invoice.getStatus().name(),
            invoice.getNotes(),
            subtotal,
            tax,
            subtotal.add(tax).setScale(2, RoundingMode.HALF_UP),
            invoice.getLines().stream().map(SalesInvoiceLineResponse::from).toList(),
            invoice.getIssuedAt(),
            invoice.getPaidAt(),
            invoice.getCreatedAt(),
            invoice.getUpdatedAt()
        );
    }

    private static BigDecimal lineBase(SalesInvoiceLine line) {
        BigDecimal subtotal = line.getQuantity().multiply(line.getUnitPrice());
        BigDecimal discount = subtotal.multiply(line.getDiscountPercent()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
        return subtotal.subtract(discount).setScale(2, RoundingMode.HALF_UP);
    }

    private static BigDecimal lineTax(SalesInvoiceLine line) {
        BigDecimal base = lineBase(line);
        return base.multiply(line.getTaxRate()).divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);
    }
}
