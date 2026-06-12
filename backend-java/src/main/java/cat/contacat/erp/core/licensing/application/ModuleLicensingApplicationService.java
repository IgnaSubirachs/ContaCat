package cat.contacat.erp.core.licensing.application;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.licensing.CompanyModuleLicense;
import cat.contacat.erp.core.licensing.CompanyModuleLicenseRepository;
import cat.contacat.erp.core.licensing.ErpModule;
import cat.contacat.erp.core.licensing.ModuleLicenseValidationException;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ModuleLicensingApplicationService {

    private final CompanyModuleLicenseRepository repository;
    private final CompanyRepository companyRepository;

    public ModuleLicensingApplicationService(
        CompanyModuleLicenseRepository repository,
        CompanyRepository companyRepository
    ) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<ModuleCatalogItem> listCatalog() {
        return Arrays.stream(ErpModule.values())
            .map(module -> new ModuleCatalogItem(
                module.getKey(),
                module.getDisplayName(),
                module.getCategory(),
                module.isDefaultEnabled()
            ))
            .sorted(Comparator.comparing(ModuleCatalogItem::category).thenComparing(ModuleCatalogItem::displayName))
            .toList();
    }

    @Transactional(readOnly = true)
    public List<CompanyModuleLicenseView> listCompanyLicenses(String companyId) {
        ensureCompanyExists(companyId);
        Map<String, CompanyModuleLicense> existing = repository.findAllByCompanyIdOrderByModuleKeyAsc(companyId).stream()
            .collect(java.util.stream.Collectors.toMap(CompanyModuleLicense::getModuleKey, Function.identity()));

        return Arrays.stream(ErpModule.values())
            .map(module -> toView(companyId, module, existing.get(module.getKey())))
            .sorted(Comparator.comparing(CompanyModuleLicenseView::category).thenComparing(CompanyModuleLicenseView::displayName))
            .toList();
    }

    @Transactional
    public CompanyModuleLicenseView upsert(String companyId, String moduleKey, CompanyModuleLicenseCommand command) {
        Company company = companyRepository.findById(companyId)
            .orElseThrow(() -> new CompanyNotFoundException(companyId));
        ErpModule module = ErpModule.fromKey(moduleKey);
        validateDates(command.startsAt(), command.expiresAt());

        CompanyModuleLicense license = repository.findByCompanyIdAndModuleKey(companyId, module.getKey())
            .orElseGet(() -> {
                CompanyModuleLicense created = new CompanyModuleLicense();
                created.setCompany(company);
                created.setModuleKey(module.getKey());
                return created;
            });

        license.setEnabled(command.enabled());
        license.setStartsAt(command.startsAt());
        license.setExpiresAt(command.expiresAt());

        return toView(companyId, module, repository.save(license));
    }

    @Transactional(readOnly = true)
    public boolean isModuleEnabled(String companyId, String moduleKey, LocalDate date) {
        ensureCompanyExists(companyId);
        ErpModule module = ErpModule.fromKey(moduleKey);
        LocalDate effectiveDate = date == null ? LocalDate.now() : date;
        return isActive(module, repository.findByCompanyIdAndModuleKey(companyId, module.getKey()).orElse(null), effectiveDate);
    }

    private CompanyModuleLicenseView toView(String companyId, ErpModule module, CompanyModuleLicense license) {
        boolean activeNow = isActive(module, license, LocalDate.now());
        return new CompanyModuleLicenseView(
            companyId,
            module.getKey(),
            module.getDisplayName(),
            module.getCategory(),
            license == null ? module.isDefaultEnabled() : license.isEnabled(),
            activeNow,
            module.isDefaultEnabled(),
            license == null ? null : license.getStartsAt(),
            license == null ? null : license.getExpiresAt(),
            license == null ? null : license.getCreatedAt(),
            license == null ? null : license.getUpdatedAt()
        );
    }

    private boolean isActive(ErpModule module, CompanyModuleLicense license, LocalDate date) {
        boolean enabled = license == null ? module.isDefaultEnabled() : license.isEnabled();
        if (!enabled) {
            return false;
        }
        if (license == null) {
            return true;
        }
        if (license.getStartsAt() != null && date.isBefore(license.getStartsAt())) {
            return false;
        }
        if (license.getExpiresAt() != null && date.isAfter(license.getExpiresAt())) {
            return false;
        }
        return true;
    }

    private void validateDates(LocalDate startsAt, LocalDate expiresAt) {
        if (startsAt != null && expiresAt != null && expiresAt.isBefore(startsAt)) {
            throw new ModuleLicenseValidationException("La data de fi de llicencia no pot ser anterior a la d'inici.");
        }
    }

    private void ensureCompanyExists(String companyId) {
        if (!companyRepository.existsById(companyId)) {
            throw new CompanyNotFoundException(companyId);
        }
    }
}
