package cat.contacat.erp.core.product.api;

import cat.contacat.erp.core.product.application.ProductApplicationService;
import cat.contacat.erp.core.product.application.ProductCommand;
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
@RequestMapping("/api/core/companies/{companyId}/products")
public class ProductController {

    private final ProductApplicationService service;

    public ProductController(ProductApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<ProductResponse> list(@PathVariable String companyId) {
        return service.list(companyId).stream().map(ProductResponse::from).toList();
    }

    @GetMapping("/{productId}")
    public ProductResponse get(@PathVariable String companyId, @PathVariable String productId) {
        return ProductResponse.from(service.get(companyId, productId));
    }

    @PostMapping
    public ResponseEntity<ProductResponse> create(
        @PathVariable String companyId,
        @Valid @RequestBody ProductRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(ProductResponse.from(service.create(companyId, toCommand(request))));
    }

    @PutMapping("/{productId}")
    public ProductResponse update(
        @PathVariable String companyId,
        @PathVariable String productId,
        @Valid @RequestBody ProductRequest request
    ) {
        return ProductResponse.from(service.update(companyId, productId, toCommand(request)));
    }

    @DeleteMapping("/{productId}")
    public ResponseEntity<Void> deactivate(@PathVariable String companyId, @PathVariable String productId) {
        service.deactivate(companyId, productId);
        return ResponseEntity.noContent().build();
    }

    private ProductCommand toCommand(ProductRequest request) {
        return new ProductCommand(
            request.sku(),
            request.name(),
            request.description(),
            request.productType(),
            request.defaultTaxCode(),
            request.salesAccountCode(),
            request.purchaseAccountCode(),
            request.active()
        );
    }
}
