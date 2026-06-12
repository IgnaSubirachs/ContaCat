package cat.contacat.erp.sales.quote.api;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;
import java.util.List;

public record QuoteRequest(
    @NotBlank String partnerId,
    @Size(max = 20) String series,
    @NotNull LocalDate quoteDate,
    @NotNull LocalDate validUntil,
    @Size(max = 4000) String notes,
    @NotEmpty List<@Valid QuoteLineRequest> lines
) {
}
