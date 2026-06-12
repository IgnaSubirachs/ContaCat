package cat.contacat.erp.core.licensing.application;

import java.time.LocalDate;
import java.time.OffsetDateTime;

public record CompanyModuleLicenseView(
    String companyId,
    String moduleKey,
    String displayName,
    String category,
    boolean enabled,
    boolean activeNow,
    boolean defaultEnabled,
    LocalDate startsAt,
    LocalDate expiresAt,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt
) {
}
