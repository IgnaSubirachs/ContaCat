package cat.contacat.erp.core.sequence.api;

import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequenceService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/core/sequences")
public class DocumentSequenceController {

    private final DocumentSequenceService service;

    public DocumentSequenceController(DocumentSequenceService service) {
        this.service = service;
    }

    @PostMapping("/next")
    public DocumentNumber next(@Valid @RequestBody NextDocumentNumberRequest request) {
        return service.allocateNext(
            request.companyId(),
            request.documentType(),
            request.series(),
            request.fiscalYear()
        );
    }
}
