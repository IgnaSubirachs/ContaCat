package cat.contacat.erp.core.product;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProductRepository extends JpaRepository<Product, String> {

    List<Product> findAllByCompanyIdOrderBySkuAsc(String companyId);

    Optional<Product> findByCompanyIdAndSku(String companyId, String sku);
}
