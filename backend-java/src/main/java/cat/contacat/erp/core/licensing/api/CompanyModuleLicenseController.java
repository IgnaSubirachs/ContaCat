package cat.contacat.erp.core.licensing.api;

import cat.contacat.erp.core.licensing.application.CompanyModuleLicenseCommand;
import cat.contacat.erp.core.licensing.application.CompanyModuleLicenseView;
import cat.contacat.erp.core.licensing.application.ModuleCatalogItem;
import cat.contacat.erp.core.licensing.application.ModuleLicensingApplicationService;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
public class CompanyModuleLicenseController {

    private final ModuleLicensingApplicationService service;

    public CompanyModuleLicenseController(ModuleLicensingApplicationService service) {
        this.service = service;
    }

    @GetMapping("/modules/catalog")
    public List<ModuleCatalogItem> listCatalog() {
        return service.listCatalog();
    }

    @GetMapping("/companies/{companyId}/module-licenses")
    public List<CompanyModuleLicenseView> listCompanyLicenses(@PathVariable String companyId) {
        return service.listCompanyLicenses(companyId);
    }

    @PutMapping("/companies/{companyId}/module-licenses/{moduleKey}")
    public CompanyModuleLicenseView updateCompanyLicense(
        @PathVariable String companyId,
        @PathVariable String moduleKey,
        @Valid @RequestBody CompanyModuleLicenseRequest request
    ) {
        return service.upsert(companyId, moduleKey, new CompanyModuleLicenseCommand(
            request.enabled(),
            request.startsAt(),
            request.expiresAt()
        ));
    }

    @GetMapping("/companies/{companyId}/module-licenses/{moduleKey}/status")
    public ModuleStatusResponse moduleStatus(
        @PathVariable String companyId,
        @PathVariable String moduleKey,
        @RequestParam(required = false) java.time.LocalDate onDate
    ) {
        return new ModuleStatusResponse(
            companyId,
            moduleKey,
            service.isModuleEnabled(companyId, moduleKey, onDate)
        );
    }
}
