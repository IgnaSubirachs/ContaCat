package cat.contacat.erp.core.sequence.api;

import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequenceNotFoundException;
import cat.contacat.erp.core.sequence.DocumentSequenceService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
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

    @ExceptionHandler(DocumentSequenceNotFoundException.class)
    public ResponseEntity<String> handleNotFound(DocumentSequenceNotFoundException exception) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(exception.getMessage());
    }
}
