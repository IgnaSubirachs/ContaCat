package cat.contacat.erp.core.partner.api;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;
import java.time.LocalDate;

public record PartnerRequest(
    @NotBlank @Size(max = 200) String name,
    @NotBlank @Size(max = 20) String taxId,
    @NotBlank @Email @Size(max = 100) String email,
    @NotBlank @Size(max = 20) String phone,
    @Size(max = 200) String tradeName,
    @Size(max = 150) String contactPerson,
    @Size(max = 20) String mobile,
    @Size(max = 255) String website,
    @Size(max = 50) String customerCode,
    @Size(max = 50) String supplierCode,
    @Size(max = 20) String relationshipStatus,
    LocalDate relationshipSince,
    @Size(max = 150) String salesRepresentative,
    @Size(max = 100) String priceList,
    @DecimalMin("0.00") @DecimalMax("100.00") BigDecimal defaultDiscount,
    @DecimalMin("0.00") BigDecimal creditLimit,
    @Min(0) Integer paymentDay,
    @Size(max = 20) String customerAccount,
    @Size(max = 20) String supplierAccount,
    @Size(max = 150) String bankName,
    @Size(max = 200) String bankAccountHolder,
    @Size(max = 11) String swiftBic,
    String contractSummary,
    String accrualNotes,
    String internalNotes,
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
