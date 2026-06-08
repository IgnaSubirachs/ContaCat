package cat.contacat.erp.core.tax.api;

import cat.contacat.erp.core.tax.TaxRateService;
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

    private final TaxRateService service;

    public TaxRateController(TaxRateService service) {
        this.service = service;
    }

    @GetMapping
    public List<TaxRateResponse> list(@PathVariable String companyId) {
        return service.list(companyId);
    }

    @GetMapping("/{taxRateId}")
    public TaxRateResponse get(@PathVariable String companyId, @PathVariable String taxRateId) {
        return service.get(companyId, taxRateId);
    }

    @PostMapping
    public ResponseEntity<TaxRateResponse> create(
        @PathVariable String companyId,
        @Valid @RequestBody TaxRateRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(companyId, request));
    }

    @PutMapping("/{taxRateId}")
    public TaxRateResponse update(
        @PathVariable String companyId,
        @PathVariable String taxRateId,
        @Valid @RequestBody TaxRateRequest request
    ) {
        return service.update(companyId, taxRateId, request);
    }

    @DeleteMapping("/{taxRateId}")
    public ResponseEntity<Void> deactivate(@PathVariable String companyId, @PathVariable String taxRateId) {
        service.deactivate(companyId, taxRateId);
        return ResponseEntity.noContent().build();
    }
}
