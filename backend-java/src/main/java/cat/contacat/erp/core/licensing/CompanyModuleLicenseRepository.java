package cat.contacat.erp.core.licensing;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CompanyModuleLicenseRepository extends JpaRepository<CompanyModuleLicense, String> {

    List<CompanyModuleLicense> findAllByCompanyIdOrderByModuleKeyAsc(String companyId);

    Optional<CompanyModuleLicense> findByCompanyIdAndModuleKey(String companyId, String moduleKey);
}
