package cat.contacat.erp.core.journal.api;

import cat.contacat.erp.core.journal.importer.InvoiceImportResult;
import cat.contacat.erp.core.journal.importer.SupplierResolutionStatus;
import java.util.List;

public record InvoiceImportResponse(
    JournalEntryResponse draftEntry,
    String supplierName,
    String supplierTaxId,
    String supplierId,
    SupplierResolutionStatus supplierResolution,
    boolean supplierCreationRequired,
    int confidence,
    List<String> warnings
) {
    public static InvoiceImportResponse from(InvoiceImportResult result) {
        return new InvoiceImportResponse(
            result.draftEntry() == null ? null : JournalEntryResponse.from(result.draftEntry()),
            result.supplierName(),
            result.supplierTaxId(),
            result.supplierId(),
            result.supplierResolution(),
            result.supplierResolution() == SupplierResolutionStatus.NOT_FOUND,
            result.confidence(),
            result.warnings()
        );
    }
}
