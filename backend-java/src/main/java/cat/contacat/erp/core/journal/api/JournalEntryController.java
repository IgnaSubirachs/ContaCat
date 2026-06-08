package cat.contacat.erp.core.journal.api;

import cat.contacat.erp.core.journal.application.JournalEntryApplicationService;
import cat.contacat.erp.core.journal.application.JournalEntryCommand;
import cat.contacat.erp.core.journal.application.JournalLineCommand;
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

    private final JournalEntryApplicationService service;

    public JournalEntryController(JournalEntryApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<JournalEntryResponse> list(
        @PathVariable String companyId,
        @RequestParam(required = false) LocalDate startDate,
        @RequestParam(required = false) LocalDate endDate
    ) {
        return service.list(companyId, startDate, endDate).stream().map(JournalEntryResponse::from).toList();
    }

    @GetMapping("/{entryId}")
    public JournalEntryResponse get(@PathVariable String companyId, @PathVariable String entryId) {
        return JournalEntryResponse.from(service.get(companyId, entryId));
    }

    @PostMapping
    public ResponseEntity<JournalEntryResponse> create(
        @PathVariable String companyId,
        @Valid @RequestBody JournalEntryRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(JournalEntryResponse.from(service.create(companyId, toCommand(request))));
    }

    @PostMapping("/{entryId}/post")
    public JournalEntryResponse post(@PathVariable String companyId, @PathVariable String entryId) {
        return JournalEntryResponse.from(service.post(companyId, entryId));
    }

    private JournalEntryCommand toCommand(JournalEntryRequest request) {
        List<JournalLineCommand> lines = request.lines().stream()
            .map(line -> new JournalLineCommand(line.accountCode(), line.debit(), line.credit(), line.description()))
            .toList();
        return new JournalEntryCommand(request.entryDate(), request.description(), request.attachmentPath(), lines);
    }
}
