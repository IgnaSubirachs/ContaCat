package cat.contacat.erp.core.tax.api;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;

public record TaxRateRequest(
    @NotBlank @Size(max = 20) String code,
    @NotBlank @Size(max = 100) String name,
    @NotNull @DecimalMin("0.00") @DecimalMax("100.00") BigDecimal rate,
    @Size(max = 20) String taxType,
    @Size(max = 20) String inputAccountCode,
    @Size(max = 20) String outputAccountCode,
    Boolean active
) {
}
