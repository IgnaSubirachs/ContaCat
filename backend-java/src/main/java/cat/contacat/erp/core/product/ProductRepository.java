package cat.contacat.erp.core.product;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProductRepository extends JpaRepository<Product, String> {

    Optional<Product> findByCompanyIdAndSku(String companyId, String sku);
}
