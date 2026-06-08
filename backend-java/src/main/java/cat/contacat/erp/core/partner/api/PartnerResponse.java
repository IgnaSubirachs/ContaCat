package cat.contacat.erp.core.partner.api;

import cat.contacat.erp.core.partner.Partner;
import java.time.OffsetDateTime;

public record PartnerResponse(
    String id,
    String companyId,
    String name,
    String taxId,
    String email,
    String phone,
    boolean supplier,
    boolean customer,
    String documentType,
    String addressStreet,
    String addressNumber,
    String addressFloor,
    String postalCode,
    String city,
    String province,
    String country,
    String vatRegime,
    boolean intraEu,
    String euVatNumber,
    String iban,
    String paymentMethod,
    int paymentDays,
    boolean active,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt
) {

    public static PartnerResponse from(Partner partner) {
        return new PartnerResponse(
            partner.getId(),
            partner.getCompany().getId(),
            partner.getName(),
            partner.getTaxId(),
            partner.getEmail(),
            partner.getPhone(),
            partner.isSupplier(),
            partner.isCustomer(),
            partner.getDocumentType(),
            partner.getAddressStreet(),
            partner.getAddressNumber(),
            partner.getAddressFloor(),
            partner.getPostalCode(),
            partner.getCity(),
            partner.getProvince(),
            partner.getCountry(),
            partner.getVatRegime(),
            partner.isIntraEu(),
            partner.getEuVatNumber(),
            partner.getIban(),
            partner.getPaymentMethod(),
            partner.getPaymentDays(),
            partner.isActive(),
            partner.getCreatedAt(),
            partner.getUpdatedAt()
        );
    }
}
