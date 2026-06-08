package cat.contacat.erp.core.account.api;

import cat.contacat.erp.core.account.AccountType;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record AccountRequest(
    @NotBlank @Size(max = 20) String code,
    @NotBlank @Size(max = 200) String name,
    @NotNull AccountType accountType,
    @Min(1) @Max(9) int group,
    String parentAccountId,
    Boolean active
) {
}
