package cat.contacat.erp.core.company.api;

import cat.contacat.erp.core.company.application.CompanyApplicationService;
import cat.contacat.erp.core.company.application.CompanyCommand;
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
@RequestMapping("/api/core/companies")
public class CompanyController {

    private final CompanyApplicationService service;

    public CompanyController(CompanyApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<CompanyResponse> list() {
        return service.list().stream().map(CompanyResponse::from).toList();
    }

    @GetMapping("/{id}")
    public CompanyResponse get(@PathVariable String id) {
        return CompanyResponse.from(service.get(id));
    }

    @PostMapping
    public ResponseEntity<CompanyResponse> create(@Valid @RequestBody CompanyRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(CompanyResponse.from(service.create(toCommand(request))));
    }

    @PutMapping("/{id}")
    public CompanyResponse update(@PathVariable String id, @Valid @RequestBody CompanyRequest request) {
        return CompanyResponse.from(service.update(id, toCommand(request)));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deactivate(@PathVariable String id) {
        service.deactivate(id);
        return ResponseEntity.noContent().build();
    }

    private CompanyCommand toCommand(CompanyRequest request) {
        return new CompanyCommand(
            request.name(),
            request.legalName(),
            request.taxId(),
            request.country(),
            request.currency(),
            request.active()
        );
    }
}
