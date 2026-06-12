package cat.contacat.erp.sales.order.api;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;

public record SalesOrderLineRequest(
    @NotBlank @Size(max = 50) String productCode,
    @NotBlank @Size(max = 500) String description,
    @NotNull @DecimalMin(value = "0.001") @Digits(integer = 11, fraction = 3) BigDecimal quantity,
    @NotNull @DecimalMin(value = "0.00") @Digits(integer = 12, fraction = 2) BigDecimal unitPrice,
    @Digits(integer = 3, fraction = 2) BigDecimal discountPercent,
    @Digits(integer = 3, fraction = 2) BigDecimal taxRate
) {
}
