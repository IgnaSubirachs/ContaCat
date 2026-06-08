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
