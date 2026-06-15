package cat.contacat.erp.sales.invoice;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SalesInvoiceRepository extends JpaRepository<SalesInvoice, String> {
    List<SalesInvoice> findAllByCompanyIdOrderByInvoiceDateDescCreatedAtDesc(String companyId);
    List<SalesInvoice> findAllByCompanyIdAndStatusOrderByInvoiceDateDescCreatedAtDesc(String companyId, SalesInvoiceStatus status);
    boolean existsBySalesOrderId(String salesOrderId);
}
