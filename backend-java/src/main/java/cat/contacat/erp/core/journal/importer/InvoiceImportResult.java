package cat.contacat.erp.core.journal.importer;

import cat.contacat.erp.core.journal.JournalEntry;
import java.util.List;

public record InvoiceImportResult(JournalEntry draftEntry, int confidence, List<String> warnings) {
}
