package cat.contacat.erp.core.product;

import cat.contacat.erp.common.BaseEntity;
import cat.contacat.erp.core.company.Company;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import jakarta.validation.constraints.NotBlank;

@Entity
@Table(name = "products", uniqueConstraints = @UniqueConstraint(name = "uq_products_company_sku", columnNames = {"company_id", "sku"}))
public class Product extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;

    @NotBlank
    @Column(nullable = false, length = 50)
    private String sku;

    @NotBlank
    @Column(nullable = false, length = 255)
    private String name;

    @Column(length = 500)
    private String description;

    @Column(name = "product_type", nullable = false, length = 20)
    private String productType = "GOOD";

    @Column(name = "default_tax_code", length = 20)
    private String defaultTaxCode;

    @Column(name = "sales_account_code", length = 20)
    private String salesAccountCode;

    @Column(name = "purchase_account_code", length = 20)
    private String purchaseAccountCode;

    @Column(name = "is_active", nullable = false)
    private boolean active = true;

    public Company getCompany() {
        return company;
    }

    public void setCompany(Company company) {
        this.company = company;
    }

    public String getSku() {
        return sku;
    }

    public void setSku(String sku) {
        this.sku = sku;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getProductType() {
        return productType;
    }

    public void setProductType(String productType) {
        this.productType = productType;
    }

    public String getDefaultTaxCode() {
        return defaultTaxCode;
    }

    public void setDefaultTaxCode(String defaultTaxCode) {
        this.defaultTaxCode = defaultTaxCode;
    }

    public String getSalesAccountCode() {
        return salesAccountCode;
    }

    public void setSalesAccountCode(String salesAccountCode) {
        this.salesAccountCode = salesAccountCode;
    }

    public String getPurchaseAccountCode() {
        return purchaseAccountCode;
    }

    public void setPurchaseAccountCode(String purchaseAccountCode) {
        this.purchaseAccountCode = purchaseAccountCode;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }
}
