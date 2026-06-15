package cat.contacat.erp.core.journal.importer;

import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.application.JournalEntryApplicationService;
import cat.contacat.erp.core.journal.application.JournalEntryCommand;
import cat.contacat.erp.core.journal.application.JournalLineCommand;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class InvoiceImportApplicationService {

    private final InvoiceDocumentReader reader;
    private final JournalEntryApplicationService journalEntryService;

    public InvoiceImportApplicationService(InvoiceDocumentReader reader, JournalEntryApplicationService journalEntryService) {
        this.reader = reader;
        this.journalEntryService = journalEntryService;
    }

    @Transactional
    public InvoiceImportResult importSupplierInvoice(String companyId, String filename, byte[] document) {
        InvoiceDocumentData data = reader.read(document);
        String description = data.invoiceNumber() == null
            ? "Factura de proveidor importada"
            : "Factura de proveidor " + data.invoiceNumber();
        if (data.supplierName() != null) {
            description += " - " + data.supplierName();
        }
        List<JournalLineCommand> lines = new ArrayList<>();
        lines.add(new JournalLineCommand("600000", data.taxableBase(), BigDecimal.ZERO, description));
        if (data.taxAmount().compareTo(BigDecimal.ZERO) > 0) {
            lines.add(new JournalLineCommand("472000", data.taxAmount(), BigDecimal.ZERO, "IVA suportat"));
        }
        lines.add(new JournalLineCommand("400000", BigDecimal.ZERO, data.total(), description));

        JournalEntry draft = journalEntryService.create(
            companyId,
            new JournalEntryCommand(data.invoiceDate(), description, filename, lines)
        );
        return new InvoiceImportResult(draft, data.confidence(), data.warnings());
    }
}
