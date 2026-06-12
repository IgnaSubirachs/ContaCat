package cat.contacat.erp.core.licensing.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.licensing.CompanyModuleLicense;
import cat.contacat.erp.core.licensing.CompanyModuleLicenseRepository;
import cat.contacat.erp.core.licensing.ModuleLicenseValidationException;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ModuleLicensingApplicationServiceTest {

    @Mock
    private CompanyModuleLicenseRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private ModuleLicensingApplicationService service;

    @Test
    void listCatalogReturnsKnownModules() {
        List<ModuleCatalogItem> catalog = service.listCatalog();

        assertThat(catalog).extracting(ModuleCatalogItem::key)
            .contains("partners", "accounting", "users");
    }

    @Test
    void listCompanyLicensesFallsBackToDefaultCatalogState() {
        when(companyRepository.existsById("company-1")).thenReturn(true);
        when(repository.findAllByCompanyIdOrderByModuleKeyAsc("company-1")).thenReturn(List.of());

        List<CompanyModuleLicenseView> licenses = service.listCompanyLicenses("company-1");

        CompanyModuleLicenseView accounting = licenses.stream()
            .filter(item -> item.moduleKey().equals("accounting"))
            .findFirst()
            .orElseThrow();

        assertThat(accounting.enabled()).isTrue();
        assertThat(accounting.activeNow()).isTrue();
        assertThat(accounting.startsAt()).isNull();
        assertThat(accounting.expiresAt()).isNull();
    }

    @Test
    void upsertCreatesOrUpdatesCompanyLicense() {
        Company company = new Company();
        company.setId("company-1");

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByCompanyIdAndModuleKey("company-1", "accounting")).thenReturn(Optional.empty());
        when(repository.save(any(CompanyModuleLicense.class))).thenAnswer(invocation -> invocation.getArgument(0));

        CompanyModuleLicenseView view = service.upsert(
            "company-1",
            "accounting",
            new CompanyModuleLicenseCommand(false, LocalDate.of(2026, 1, 1), LocalDate.of(2026, 12, 31))
        );

        assertThat(view.companyId()).isEqualTo("company-1");
        assertThat(view.moduleKey()).isEqualTo("accounting");
        assertThat(view.enabled()).isFalse();
        assertThat(view.startsAt()).isEqualTo(LocalDate.of(2026, 1, 1));
        assertThat(view.expiresAt()).isEqualTo(LocalDate.of(2026, 12, 31));
    }

    @Test
    void upsertRejectsInvalidDateRange() {
        Company company = new Company();
        company.setId("company-1");

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));

        assertThatThrownBy(() -> service.upsert(
            "company-1",
            "accounting",
            new CompanyModuleLicenseCommand(true, LocalDate.of(2026, 12, 31), LocalDate.of(2026, 1, 1))
        )).isInstanceOf(ModuleLicenseValidationException.class);
    }

    @Test
    void isModuleEnabledHonoursExplicitDisable() {
        CompanyModuleLicense license = new CompanyModuleLicense();
        license.setEnabled(false);
        license.setModuleKey("partners");

        when(companyRepository.existsById("company-1")).thenReturn(true);
        when(repository.findByCompanyIdAndModuleKey("company-1", "partners")).thenReturn(Optional.of(license));

        assertThat(service.isModuleEnabled("company-1", "partners", LocalDate.of(2026, 6, 12))).isFalse();
    }

    @Test
    void isModuleEnabledFailsForUnknownCompany() {
        when(companyRepository.existsById("missing-company")).thenReturn(false);

        assertThatThrownBy(() -> service.isModuleEnabled("missing-company", "partners", LocalDate.now()))
            .isInstanceOf(CompanyNotFoundException.class);
        verify(companyRepository).existsById("missing-company");
    }
}
