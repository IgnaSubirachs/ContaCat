package cat.contacat.erp.core.journal.importer;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public record InvoiceDocumentData(
    LocalDate invoiceDate,
    String supplierName,
    String supplierTaxId,
    String invoiceNumber,
    BigDecimal taxableBase,
    BigDecimal taxAmount,
    BigDecimal total,
    int confidence,
    List<String> warnings
) {
}
