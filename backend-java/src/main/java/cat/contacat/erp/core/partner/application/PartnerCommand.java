package cat.contacat.erp.core.partner.application;

public record PartnerCommand(
    String name,
    String taxId,
    String email,
    String phone,
    Boolean isSupplier,
    Boolean isCustomer,
    String documentType,
    String addressStreet,
    String addressNumber,
    String addressFloor,
    String postalCode,
    String city,
    String province,
    String country,
    String vatRegime,
    Boolean isIntraEu,
    String euVatNumber,
    String iban,
    String paymentMethod,
    Integer paymentDays,
    Boolean active
) {
}
