package cat.contacat.erp.core.journal.api;

import cat.contacat.erp.core.journal.JournalEntryValidationException;
import cat.contacat.erp.core.journal.importer.InvoiceImportApplicationService;
import java.io.IOException;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/core/companies/{companyId}/journal-entry-imports")
public class InvoiceImportController {

    private final InvoiceImportApplicationService service;

    public InvoiceImportController(InvoiceImportApplicationService service) {
        this.service = service;
    }

    @PostMapping(path = "/supplier-invoice-pdf", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public InvoiceImportResponse importSupplierInvoice(
        @PathVariable String companyId,
        @RequestPart("file") MultipartFile file
    ) {
        if (!MediaType.APPLICATION_PDF_VALUE.equalsIgnoreCase(file.getContentType())) {
            throw new JournalEntryValidationException("El document ha de ser un PDF");
        }
        try {
            return InvoiceImportResponse.from(service.importSupplierInvoice(companyId, file.getOriginalFilename(), file.getBytes()));
        } catch (IOException exception) {
            throw new JournalEntryValidationException("No s'ha pogut llegir el fitxer rebut");
        }
    }
}
