package cat.contacat.erp.core.warehouse;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WarehouseRepository extends JpaRepository<Warehouse, String> {

    List<Warehouse> findAllByCompanyIdOrderByCodeAsc(String companyId);

    Optional<Warehouse> findByCompanyIdAndCode(String companyId, String code);
}
