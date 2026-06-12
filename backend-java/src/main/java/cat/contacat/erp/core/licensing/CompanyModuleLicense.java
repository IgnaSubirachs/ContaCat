package cat.contacat.erp.core.licensing;

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
import java.time.LocalDate;
import java.time.OffsetDateTime;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

@Entity
@Table(
    name = "company_module_licenses",
    uniqueConstraints = @UniqueConstraint(name = "uq_company_module_licenses_scope", columnNames = {"company_id", "module_key"}),
    indexes = {
        @Index(name = "ix_company_module_licenses_company", columnList = "company_id"),
        @Index(name = "ix_company_module_licenses_module", columnList = "module_key")
    }
)
public class CompanyModuleLicense extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;

    @Column(name = "module_key", nullable = false, length = 50)
    private String moduleKey;

    @Column(name = "is_enabled", nullable = false)
    private boolean enabled = true;

    @Column(name = "starts_at")
    private LocalDate startsAt;

    @Column(name = "expires_at")
    private LocalDate expiresAt;

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

    public String getModuleKey() {
        return moduleKey;
    }

    public void setModuleKey(String moduleKey) {
        this.moduleKey = moduleKey;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public LocalDate getStartsAt() {
        return startsAt;
    }

    public void setStartsAt(LocalDate startsAt) {
        this.startsAt = startsAt;
    }

    public LocalDate getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(LocalDate expiresAt) {
        this.expiresAt = expiresAt;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public OffsetDateTime getUpdatedAt() {
        return updatedAt;
    }
}
