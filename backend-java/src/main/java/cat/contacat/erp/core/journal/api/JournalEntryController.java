package cat.contacat.erp.core.journal.api;

import cat.contacat.erp.core.journal.JournalEntryService;
import jakarta.validation.Valid;
import java.time.LocalDate;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/core/companies/{companyId}/journal-entries")
public class JournalEntryController {

    private final JournalEntryService service;

    public JournalEntryController(JournalEntryService service) {
        this.service = service;
    }

    @GetMapping
    public List<JournalEntryResponse> list(
        @PathVariable String companyId,
        @RequestParam(required = false) LocalDate startDate,
        @RequestParam(required = false) LocalDate endDate
    ) {
        return service.list(companyId, startDate, endDate);
    }

    @GetMapping("/{entryId}")
    public JournalEntryResponse get(@PathVariable String companyId, @PathVariable String entryId) {
        return service.get(companyId, entryId);
    }

    @PostMapping
    public ResponseEntity<JournalEntryResponse> create(
        @PathVariable String companyId,
        @Valid @RequestBody JournalEntryRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(companyId, request));
    }

    @PostMapping("/{entryId}/post")
    public JournalEntryResponse post(@PathVariable String companyId, @PathVariable String entryId) {
        return service.post(companyId, entryId);
    }
}
