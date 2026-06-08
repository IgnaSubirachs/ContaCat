package cat.contacat.erp.core.company.application;

public record CompanyCommand(
    String name,
    String legalName,
    String taxId,
    String country,
    String currency,
    Boolean active
) {
}
