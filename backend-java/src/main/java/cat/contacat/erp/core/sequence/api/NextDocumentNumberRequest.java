package cat.contacat.erp.core.sequence.api;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record NextDocumentNumberRequest(
    @NotBlank String companyId,
    @NotBlank String documentType,
    String series,
    @Min(2000) int fiscalYear
) {
}
