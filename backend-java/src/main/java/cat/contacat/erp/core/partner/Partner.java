package cat.contacat.erp.core.partner;

import cat.contacat.erp.common.BaseEntity;
import cat.contacat.erp.core.company.Company;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Index;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.LocalDate;
import jakarta.persistence.UniqueConstraint;
import java.time.OffsetDateTime;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

@Entity
@Table(
    name = "partners",
    uniqueConstraints = @UniqueConstraint(name = "uq_partners_company_tax_id", columnNames = {"company_id", "tax_id"}),
    indexes = {
        @Index(name = "ix_partners_company_name", columnList = "company_id, name"),
        @Index(name = "ix_partners_company_customer", columnList = "company_id, is_customer"),
        @Index(name = "ix_partners_company_supplier", columnList = "company_id, is_supplier")
    }
)
public class Partner extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(name = "tax_id", nullable = false, length = 20)
    private String taxId;

    @Column(nullable = false, length = 100)
    private String email;

    @Column(nullable = false, length = 20)
    private String phone;

    @Column(name = "trade_name", nullable = false, length = 200)
    private String tradeName = "";

    @Column(name = "contact_person", nullable = false, length = 150)
    private String contactPerson = "";

    @Column(nullable = false, length = 20)
    private String mobile = "";

    @Column(nullable = false, length = 255)
    private String website = "";

    @Column(name = "customer_code", nullable = false, length = 50)
    private String customerCode = "";

    @Column(name = "supplier_code", nullable = false, length = 50)
    private String supplierCode = "";

    @Column(name = "relationship_status", nullable = false, length = 20)
    private String relationshipStatus = "ACTIVE";

    @Column(name = "relationship_since")
    private LocalDate relationshipSince;

    @Column(name = "sales_representative", nullable = false, length = 150)
    private String salesRepresentative = "";

    @Column(name = "price_list", nullable = false, length = 100)
    private String priceList = "";

    @Column(name = "default_discount", nullable = false, precision = 8, scale = 2)
    private BigDecimal defaultDiscount = BigDecimal.ZERO;

    @Column(name = "credit_limit", nullable = false, precision = 12, scale = 2)
    private BigDecimal creditLimit = BigDecimal.ZERO;

    @Column(name = "payment_day", nullable = false)
    private int paymentDay;

    @Column(name = "customer_account", nullable = false, length = 20)
    private String customerAccount = "";

    @Column(name = "supplier_account", nullable = false, length = 20)
    private String supplierAccount = "";

    @Column(name = "bank_name", nullable = false, length = 150)
    private String bankName = "";

    @Column(name = "bank_account_holder", nullable = false, length = 200)
    private String bankAccountHolder = "";

    @Column(name = "swift_bic", nullable = false, length = 11)
    private String swiftBic = "";

    @Column(name = "contract_summary", nullable = false, columnDefinition = "TEXT")
    private String contractSummary = "";

    @Column(name = "accrual_notes", nullable = false, columnDefinition = "TEXT")
    private String accrualNotes = "";

    @Column(name = "internal_notes", nullable = false, columnDefinition = "TEXT")
    private String internalNotes = "";

    @Column(name = "is_supplier", nullable = false)
    private boolean supplier;

    @Column(name = "is_customer", nullable = false)
    private boolean customer;

    @Column(name = "document_type", nullable = false, length = 20)
    private String documentType = "NIF";

    @Column(name = "address_street", nullable = false, length = 200)
    private String addressStreet = "";

    @Column(name = "address_number", nullable = false, length = 20)
    private String addressNumber = "";

    @Column(name = "address_floor", nullable = false, length = 50)
    private String addressFloor = "";

    @Column(name = "postal_code", nullable = false, length = 10)
    private String postalCode = "";

    @Column(nullable = false, length = 100)
    private String city = "";

    @Column(nullable = false, length = 100)
    private String province = "";

    @Column(nullable = false, length = 100)
    private String country = "Espanya";

    @Column(name = "vat_regime", nullable = false, length = 50)
    private String vatRegime = "GENERAL";

    @Column(name = "is_intra_eu", nullable = false)
    private boolean intraEu;

    @Column(name = "eu_vat_number", nullable = false, length = 30)
    private String euVatNumber = "";

    @Column(nullable = false, length = 34)
    private String iban = "";

    @Column(name = "payment_method", nullable = false, length = 50)
    private String paymentMethod = "TRANSFER";

    @Column(name = "payment_days", nullable = false)
    private int paymentDays = 30;

    @Column(name = "is_active", nullable = false)
    private boolean active = true;

    @CreationTimestamp
    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private OffsetDateTime updatedAt;

    public Company getCompany() {
        return company;
    }

    public void setCompany(Company company) {
        this.company = company;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getTaxId() {
        return taxId;
    }

    public void setTaxId(String taxId) {
        this.taxId = taxId;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getTradeName() {
        return tradeName;
    }

    public void setTradeName(String tradeName) {
        this.tradeName = tradeName;
    }

    public String getContactPerson() {
        return contactPerson;
    }

    public void setContactPerson(String contactPerson) {
        this.contactPerson = contactPerson;
    }

    public String getMobile() {
        return mobile;
    }

    public void setMobile(String mobile) {
        this.mobile = mobile;
    }

    public String getWebsite() {
        return website;
    }

    public void setWebsite(String website) {
        this.website = website;
    }

    public String getCustomerCode() {
        return customerCode;
    }

    public void setCustomerCode(String customerCode) {
        this.customerCode = customerCode;
    }

    public String getSupplierCode() {
        return supplierCode;
    }

    public void setSupplierCode(String supplierCode) {
        this.supplierCode = supplierCode;
    }

    public String getRelationshipStatus() {
        return relationshipStatus;
    }

    public void setRelationshipStatus(String relationshipStatus) {
        this.relationshipStatus = relationshipStatus;
    }

    public LocalDate getRelationshipSince() {
        return relationshipSince;
    }

    public void setRelationshipSince(LocalDate relationshipSince) {
        this.relationshipSince = relationshipSince;
    }

    public String getSalesRepresentative() {
        return salesRepresentative;
    }

    public void setSalesRepresentative(String salesRepresentative) {
        this.salesRepresentative = salesRepresentative;
    }

    public String getPriceList() {
        return priceList;
    }

    public void setPriceList(String priceList) {
        this.priceList = priceList;
    }

    public BigDecimal getDefaultDiscount() {
        return defaultDiscount;
    }

    public void setDefaultDiscount(BigDecimal defaultDiscount) {
        this.defaultDiscount = defaultDiscount;
    }

    public BigDecimal getCreditLimit() {
        return creditLimit;
    }

    public void setCreditLimit(BigDecimal creditLimit) {
        this.creditLimit = creditLimit;
    }

    public int getPaymentDay() {
        return paymentDay;
    }

    public void setPaymentDay(int paymentDay) {
        this.paymentDay = paymentDay;
    }

    public String getCustomerAccount() {
        return customerAccount;
    }

    public void setCustomerAccount(String customerAccount) {
        this.customerAccount = customerAccount;
    }

    public String getSupplierAccount() {
        return supplierAccount;
    }

    public void setSupplierAccount(String supplierAccount) {
        this.supplierAccount = supplierAccount;
    }

    public String getBankName() {
        return bankName;
    }

    public void setBankName(String bankName) {
        this.bankName = bankName;
    }

    public String getBankAccountHolder() {
        return bankAccountHolder;
    }

    public void setBankAccountHolder(String bankAccountHolder) {
        this.bankAccountHolder = bankAccountHolder;
    }

    public String getSwiftBic() {
        return swiftBic;
    }

    public void setSwiftBic(String swiftBic) {
        this.swiftBic = swiftBic;
    }

    public String getContractSummary() {
        return contractSummary;
    }

    public void setContractSummary(String contractSummary) {
        this.contractSummary = contractSummary;
    }

    public String getAccrualNotes() {
        return accrualNotes;
    }

    public void setAccrualNotes(String accrualNotes) {
        this.accrualNotes = accrualNotes;
    }

    public String getInternalNotes() {
        return internalNotes;
    }

    public void setInternalNotes(String internalNotes) {
        this.internalNotes = internalNotes;
    }

    public boolean isSupplier() {
        return supplier;
    }

    public void setSupplier(boolean supplier) {
        this.supplier = supplier;
    }

    public boolean isCustomer() {
        return customer;
    }

    public void setCustomer(boolean customer) {
        this.customer = customer;
    }

    public String getDocumentType() {
        return documentType;
    }

    public void setDocumentType(String documentType) {
        this.documentType = documentType;
    }

    public String getAddressStreet() {
        return addressStreet;
    }

    public void setAddressStreet(String addressStreet) {
        this.addressStreet = addressStreet;
    }

    public String getAddressNumber() {
        return addressNumber;
    }

    public void setAddressNumber(String addressNumber) {
        this.addressNumber = addressNumber;
    }

    public String getAddressFloor() {
        return addressFloor;
    }

    public void setAddressFloor(String addressFloor) {
        this.addressFloor = addressFloor;
    }

    public String getPostalCode() {
        return postalCode;
    }

    public void setPostalCode(String postalCode) {
        this.postalCode = postalCode;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getProvince() {
        return province;
    }

    public void setProvince(String province) {
        this.province = province;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    public String getVatRegime() {
        return vatRegime;
    }

    public void setVatRegime(String vatRegime) {
        this.vatRegime = vatRegime;
    }

    public boolean isIntraEu() {
        return intraEu;
    }

    public void setIntraEu(boolean intraEu) {
        this.intraEu = intraEu;
    }

    public String getEuVatNumber() {
        return euVatNumber;
    }

    public void setEuVatNumber(String euVatNumber) {
        this.euVatNumber = euVatNumber;
    }

    public String getIban() {
        return iban;
    }

    public void setIban(String iban) {
        this.iban = iban;
    }

    public String getPaymentMethod() {
        return paymentMethod;
    }

    public void setPaymentMethod(String paymentMethod) {
        this.paymentMethod = paymentMethod;
    }

    public int getPaymentDays() {
        return paymentDays;
    }

    public void setPaymentDays(int paymentDays) {
        this.paymentDays = paymentDays;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public OffsetDateTime getUpdatedAt() {
        return updatedAt;
    }
}
