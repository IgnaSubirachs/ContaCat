package cat.contacat.erp.sales.quote.api;

import cat.contacat.erp.sales.quote.application.QuoteApplicationService;
import cat.contacat.erp.sales.quote.application.QuoteCommand;
import cat.contacat.erp.sales.quote.application.QuoteLineCommand;
import jakarta.validation.Valid;
import java.time.LocalDate;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/sales/companies/{companyId}/quotes")
public class QuoteController {

    private final QuoteApplicationService service;

    public QuoteController(QuoteApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<QuoteResponse> list(
        @PathVariable String companyId,
        @RequestParam(required = false) String status,
        @RequestParam(required = false) LocalDate startDate,
        @RequestParam(required = false) LocalDate endDate
    ) {
        return service.list(companyId, status, startDate, endDate).stream().map(QuoteResponse::from).toList();
    }

    @GetMapping("/{quoteId}")
    public QuoteResponse get(@PathVariable String companyId, @PathVariable String quoteId) {
        return QuoteResponse.from(service.get(companyId, quoteId));
    }

    @PostMapping
    public ResponseEntity<QuoteResponse> create(@PathVariable String companyId, @Valid @RequestBody QuoteRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(QuoteResponse.from(service.create(companyId, toCommand(request))));
    }

    @PutMapping("/{quoteId}")
    public QuoteResponse update(
        @PathVariable String companyId,
        @PathVariable String quoteId,
        @Valid @RequestBody QuoteRequest request
    ) {
        return QuoteResponse.from(service.update(companyId, quoteId, toCommand(request)));
    }

    @PostMapping("/{quoteId}/send")
    public QuoteResponse send(@PathVariable String companyId, @PathVariable String quoteId) {
        return QuoteResponse.from(service.send(companyId, quoteId));
    }

    @PostMapping("/{quoteId}/accept")
    public QuoteResponse accept(@PathVariable String companyId, @PathVariable String quoteId) {
        return QuoteResponse.from(service.accept(companyId, quoteId));
    }

    @PostMapping("/{quoteId}/reject")
    public QuoteResponse reject(@PathVariable String companyId, @PathVariable String quoteId) {
        return QuoteResponse.from(service.reject(companyId, quoteId));
    }

    @DeleteMapping("/{quoteId}")
    public ResponseEntity<Void> delete(@PathVariable String companyId, @PathVariable String quoteId) {
        service.delete(companyId, quoteId);
        return ResponseEntity.noContent().build();
    }

    private QuoteCommand toCommand(QuoteRequest request) {
        return new QuoteCommand(
            request.partnerId(),
            request.series(),
            request.quoteDate(),
            request.validUntil(),
            request.notes(),
            request.lines().stream()
                .map(line -> new QuoteLineCommand(
                    line.productCode(),
                    line.description(),
                    line.quantity(),
                    line.unitPrice(),
                    line.discountPercent(),
                    line.taxRate()
                ))
                .toList()
        );
    }
}
