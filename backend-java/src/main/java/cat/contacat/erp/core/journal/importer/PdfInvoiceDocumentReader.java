package cat.contacat.erp.core.journal.importer;

import cat.contacat.erp.core.journal.JournalEntryValidationException;
import java.io.IOException;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Component;

@Component
public class PdfInvoiceDocumentReader implements InvoiceDocumentReader {

    private final InvoiceTextInterpreter interpreter;

    public PdfInvoiceDocumentReader(InvoiceTextInterpreter interpreter) {
        this.interpreter = interpreter;
    }

    @Override
    public InvoiceDocumentData read(byte[] document) {
        try (var pdf = Loader.loadPDF(document)) {
            return interpreter.interpret(new PDFTextStripper().getText(pdf));
        } catch (IOException exception) {
            throw new JournalEntryValidationException("No s'ha pogut llegir el document PDF");
        }
    }
}
