package cat.contacat.erp.sales.order;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SalesOrderRepository extends JpaRepository<SalesOrder, String> {
    List<SalesOrder> findAllByCompanyIdOrderByOrderDateDescOrderNumberDesc(String companyId);
    List<SalesOrder> findAllByCompanyIdAndStatusOrderByOrderDateDescOrderNumberDesc(String companyId, SalesOrderStatus status);
}
