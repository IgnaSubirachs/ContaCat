package cat.contacat.erp.core.warehouse.api;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record WarehouseRequest(
    @NotBlank @Size(max = 50) String code,
    @NotBlank @Size(max = 255) String name,
    Boolean active
) {
}
