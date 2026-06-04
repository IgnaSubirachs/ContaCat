package cat.contacat.erp.core.tax;

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
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;

@Entity
@Table(name = "tax_rates", uniqueConstraints = @UniqueConstraint(name = "uq_tax_rates_company_code", columnNames = {"company_id", "code"}))
public class TaxRate extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;

    @NotBlank
    @Column(nullable = false, length = 20)
    private String code;

    @NotBlank
    @Column(nullable = false, length = 100)
    private String name;

    @NotNull
    @Column(nullable = false, precision = 5, scale = 2)
    private BigDecimal rate;

    @Column(name = "tax_type", nullable = false, length = 20)
    private String taxType = "VAT";

    @Column(name = "input_account_code", length = 20)
    private String inputAccountCode;

    @Column(name = "output_account_code", length = 20)
    private String outputAccountCode;

    @Column(name = "is_active", nullable = false)
    private boolean active = true;

    public Company getCompany() {
        return company;
    }

    public void setCompany(Company company) {
        this.company = company;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public BigDecimal getRate() {
        return rate;
    }

    public void setRate(BigDecimal rate) {
        this.rate = rate;
    }

    public String getTaxType() {
        return taxType;
    }

    public void setTaxType(String taxType) {
        this.taxType = taxType;
    }

    public String getInputAccountCode() {
        return inputAccountCode;
    }

    public void setInputAccountCode(String inputAccountCode) {
        this.inputAccountCode = inputAccountCode;
    }

    public String getOutputAccountCode() {
        return outputAccountCode;
    }

    public void setOutputAccountCode(String outputAccountCode) {
        this.outputAccountCode = outputAccountCode;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }
}
