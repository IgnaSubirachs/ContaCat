package cat.contacat.erp.core.product.api;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record ProductRequest(
    @NotBlank @Size(max = 50) String sku,
    @NotBlank @Size(max = 255) String name,
    @Size(max = 500) String description,
    @Size(max = 20) String productType,
    @Size(max = 20) String defaultTaxCode,
    @Size(max = 20) String salesAccountCode,
    @Size(max = 20) String purchaseAccountCode,
    Boolean active
) {
}
