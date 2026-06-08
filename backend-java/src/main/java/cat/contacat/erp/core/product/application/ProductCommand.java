package cat.contacat.erp.core.product.application;

public record ProductCommand(
    String sku,
    String name,
    String description,
    String productType,
    String defaultTaxCode,
    String salesAccountCode,
    String purchaseAccountCode,
    Boolean active
) {
}
