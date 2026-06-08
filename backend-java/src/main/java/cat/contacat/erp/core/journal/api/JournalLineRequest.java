package cat.contacat.erp.core.journal.api;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;

public record JournalLineRequest(
    @NotBlank @Size(max = 20) String accountCode,
    @NotNull @DecimalMin("0.00") BigDecimal debit,
    @NotNull @DecimalMin("0.00") BigDecimal credit,
    @Size(max = 500) String description
) {
}
