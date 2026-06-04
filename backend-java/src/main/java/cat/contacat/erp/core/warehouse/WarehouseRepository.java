package cat.contacat.erp.core.warehouse;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WarehouseRepository extends JpaRepository<Warehouse, String> {

    Optional<Warehouse> findByCompanyIdAndCode(String companyId, String code);
}
