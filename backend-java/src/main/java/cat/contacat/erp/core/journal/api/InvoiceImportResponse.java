package cat.contacat.erp.core.journal.api;

import cat.contacat.erp.core.journal.importer.InvoiceImportResult;
import java.util.List;

public record InvoiceImportResponse(JournalEntryResponse draftEntry, int confidence, List<String> warnings) {
    public static InvoiceImportResponse from(InvoiceImportResult result) {
        return new InvoiceImportResponse(
            JournalEntryResponse.from(result.draftEntry()),
            result.confidence(),
            result.warnings()
        );
    }
}
