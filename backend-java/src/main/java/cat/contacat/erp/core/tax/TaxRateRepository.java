package cat.contacat.erp.core.tax;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TaxRateRepository extends JpaRepository<TaxRate, String> {

    Optional<TaxRate> findByCompanyIdAndCode(String companyId, String code);
}
