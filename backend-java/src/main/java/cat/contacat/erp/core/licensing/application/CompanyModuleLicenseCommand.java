package cat.contacat.erp.core.licensing.application;

import java.time.LocalDate;

public record CompanyModuleLicenseCommand(
    boolean enabled,
    LocalDate startsAt,
    LocalDate expiresAt
) {
}
