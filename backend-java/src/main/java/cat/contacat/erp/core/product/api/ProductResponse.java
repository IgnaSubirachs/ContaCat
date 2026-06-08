package cat.contacat.erp.core.product.api;

import cat.contacat.erp.core.product.Product;

public record ProductResponse(
    String id,
    String companyId,
    String sku,
    String name,
    String description,
    String productType,
    String defaultTaxCode,
    String salesAccountCode,
    String purchaseAccountCode,
    boolean active
) {

    public static ProductResponse from(Product product) {
        return new ProductResponse(
            product.getId(),
            product.getCompany().getId(),
            product.getSku(),
            product.getName(),
            product.getDescription(),
            product.getProductType(),
            product.getDefaultTaxCode(),
            product.getSalesAccountCode(),
            product.getPurchaseAccountCode(),
            product.isActive()
        );
    }
}
