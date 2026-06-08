package cat.contacat.erp.core.tax.api;

import cat.contacat.erp.core.tax.application.TaxRateApplicationService;
import cat.contacat.erp.core.tax.application.TaxRateCommand;
import jakarta.validation.Valid;
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
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/core/companies/{companyId}/tax-rates")
public class TaxRateController {

    private final TaxRateApplicationService service;

    public TaxRateController(TaxRateApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<TaxRateResponse> list(@PathVariable String companyId) {
        return service.list(companyId).stream().map(TaxRateResponse::from).toList();
    }

    @GetMapping("/{taxRateId}")
    public TaxRateResponse get(@PathVariable String companyId, @PathVariable String taxRateId) {
        return TaxRateResponse.from(service.get(companyId, taxRateId));
    }

    @PostMapping
    public ResponseEntity<TaxRateResponse> create(
        @PathVariable String companyId,
        @Valid @RequestBody TaxRateRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(TaxRateResponse.from(service.create(companyId, toCommand(request))));
    }

    @PutMapping("/{taxRateId}")
    public TaxRateResponse update(
        @PathVariable String companyId,
        @PathVariable String taxRateId,
        @Valid @RequestBody TaxRateRequest request
    ) {
        return TaxRateResponse.from(service.update(companyId, taxRateId, toCommand(request)));
    }

    @DeleteMapping("/{taxRateId}")
    public ResponseEntity<Void> deactivate(@PathVariable String companyId, @PathVariable String taxRateId) {
        service.deactivate(companyId, taxRateId);
        return ResponseEntity.noContent().build();
    }

    private TaxRateCommand toCommand(TaxRateRequest request) {
        return new TaxRateCommand(
            request.code(),
            request.name(),
            request.rate(),
            request.taxType(),
            request.inputAccountCode(),
            request.outputAccountCode(),
            request.active()
        );
    }
}
