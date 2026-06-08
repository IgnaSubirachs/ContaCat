package cat.contacat.erp.core.tax;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TaxRateRepository extends JpaRepository<TaxRate, String> {

    List<TaxRate> findAllByCompanyIdOrderByCodeAsc(String companyId);

    Optional<TaxRate> findByCompanyIdAndCode(String companyId, String code);
}
