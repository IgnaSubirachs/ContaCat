package cat.contacat.erp.core.partner.api;

import cat.contacat.erp.core.partner.PartnerService;
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
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/core/companies/{companyId}/partners")
public class PartnerController {

    private final PartnerService service;

    public PartnerController(PartnerService service) {
        this.service = service;
    }

    @GetMapping
    public List<PartnerResponse> list(
        @PathVariable String companyId,
        @RequestParam(required = false) String role
    ) {
        return service.list(companyId, role);
    }

    @GetMapping("/{partnerId}")
    public PartnerResponse get(@PathVariable String companyId, @PathVariable String partnerId) {
        return service.get(companyId, partnerId);
    }

    @PostMapping
    public ResponseEntity<PartnerResponse> create(
        @PathVariable String companyId,
        @Valid @RequestBody PartnerRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(companyId, request));
    }

    @PutMapping("/{partnerId}")
    public PartnerResponse update(
        @PathVariable String companyId,
        @PathVariable String partnerId,
        @Valid @RequestBody PartnerRequest request
    ) {
        return service.update(companyId, partnerId, request);
    }

    @DeleteMapping("/{partnerId}")
    public ResponseEntity<Void> deactivate(@PathVariable String companyId, @PathVariable String partnerId) {
        service.deactivate(companyId, partnerId);
        return ResponseEntity.noContent().build();
    }
}
