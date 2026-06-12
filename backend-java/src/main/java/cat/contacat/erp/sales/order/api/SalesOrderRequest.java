package cat.contacat.erp.sales.order.api;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;
import java.util.List;

public record SalesOrderRequest(
    @NotBlank String partnerId,
    @Size(max = 20) String series,
    @NotNull LocalDate orderDate,
    LocalDate deliveryDate,
    @Size(max = 500) String deliveryAddress,
    @Size(max = 4000) String notes,
    @NotEmpty List<@Valid SalesOrderLineRequest> lines
) {
}
