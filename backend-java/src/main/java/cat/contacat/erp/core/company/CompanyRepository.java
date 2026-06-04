package cat.contacat.erp.core.company;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CompanyRepository extends JpaRepository<Company, String> {

    Optional<Company> findByTaxId(String taxId);
}
