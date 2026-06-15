package cat.contacat.erp.sales.invoice.api;

import java.time.LocalDate;

public record CreateInvoiceFromOrderRequest(LocalDate invoiceDate, LocalDate dueDate) {
}
