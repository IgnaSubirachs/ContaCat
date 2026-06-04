package cat.contacat.erp.core.company.api;

import cat.contacat.erp.core.company.Company;
import java.time.OffsetDateTime;

public record CompanyResponse(
    String id,
    String name,
    String legalName,
    String taxId,
    String country,
    String currency,
    boolean active,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt
) {

    public static CompanyResponse from(Company company) {
        return new CompanyResponse(
            company.getId(),
            company.getName(),
            company.getLegalName(),
            company.getTaxId(),
            company.getCountry(),
            company.getCurrency(),
            company.isActive(),
            company.getCreatedAt(),
            company.getUpdatedAt()
        );
    }
}
