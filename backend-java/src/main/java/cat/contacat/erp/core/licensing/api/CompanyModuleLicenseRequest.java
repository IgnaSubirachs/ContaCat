package cat.contacat.erp.core.licensing.api;

import java.time.LocalDate;

public record CompanyModuleLicenseRequest(
    boolean enabled,
    LocalDate startsAt,
    LocalDate expiresAt
) {
}
