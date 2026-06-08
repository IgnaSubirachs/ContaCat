package cat.contacat.erp.core.partner.api;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record PartnerRequest(
    @NotBlank @Size(max = 200) String name,
    @NotBlank @Size(max = 20) String taxId,
    @NotBlank @Email @Size(max = 100) String email,
    @NotBlank @Size(max = 20) String phone,
    @NotNull Boolean isSupplier,
    @NotNull Boolean isCustomer,
    @Size(max = 20) String documentType,
    @Size(max = 200) String addressStreet,
    @Size(max = 20) String addressNumber,
    @Size(max = 50) String addressFloor,
    @Size(max = 10) String postalCode,
    @Size(max = 100) String city,
    @Size(max = 100) String province,
    @Size(max = 100) String country,
    @Size(max = 50) String vatRegime,
    Boolean isIntraEu,
    @Size(max = 30) String euVatNumber,
    @Size(max = 34) String iban,
    @Size(max = 50) String paymentMethod,
    @Min(0) Integer paymentDays,
    Boolean active
) {
}
