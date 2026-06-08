package cat.contacat.erp.core.partner;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PartnerRepository extends JpaRepository<Partner, String> {

    List<Partner> findAllByCompanyIdOrderByNameAsc(String companyId);

    List<Partner> findAllByCompanyIdAndCustomerTrueOrderByNameAsc(String companyId);

    List<Partner> findAllByCompanyIdAndSupplierTrueOrderByNameAsc(String companyId);

    Optional<Partner> findByCompanyIdAndTaxId(String companyId, String taxId);
}
