package cat.contacat.erp.core.company.api;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CompanyRequest(
    @NotBlank @Size(max = 255) String name,
    @NotBlank @Size(max = 255) String legalName,
    @NotBlank @Size(max = 50) String taxId,
    @Size(max = 2) String country,
    @Size(max = 3) String currency,
    Boolean active
) {
}
