package cat.contacat.erp.sales.invoice.api;

import cat.contacat.erp.sales.invoice.application.SalesInvoiceApplicationService;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/sales/companies/{companyId}/invoices")
public class SalesInvoiceController {

    private final SalesInvoiceApplicationService service;

    public SalesInvoiceController(SalesInvoiceApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<SalesInvoiceResponse> list(@PathVariable String companyId, @RequestParam(required = false) String status) {
        return service.list(companyId, status).stream().map(SalesInvoiceResponse::from).toList();
    }

    @GetMapping("/{invoiceId}")
    public SalesInvoiceResponse get(@PathVariable String companyId, @PathVariable String invoiceId) {
        return SalesInvoiceResponse.from(service.get(companyId, invoiceId));
    }

    @PostMapping("/from-order/{orderId}")
    public ResponseEntity<SalesInvoiceResponse> createFromOrder(
        @PathVariable String companyId,
        @PathVariable String orderId,
        @RequestBody(required = false) CreateInvoiceFromOrderRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(SalesInvoiceResponse.from(service.createFromOrder(
            companyId,
            orderId,
            request == null ? null : request.invoiceDate(),
            request == null ? null : request.dueDate()
        )));
    }

    @PostMapping("/{invoiceId}/issue")
    public SalesInvoiceResponse issue(@PathVariable String companyId, @PathVariable String invoiceId) {
        return SalesInvoiceResponse.from(service.issue(companyId, invoiceId));
    }

    @PostMapping("/{invoiceId}/paid")
    public SalesInvoiceResponse markPaid(@PathVariable String companyId, @PathVariable String invoiceId) {
        return SalesInvoiceResponse.from(service.markPaid(companyId, invoiceId));
    }

    @DeleteMapping("/{invoiceId}")
    public ResponseEntity<Void> deleteDraft(@PathVariable String companyId, @PathVariable String invoiceId) {
        service.deleteDraft(companyId, invoiceId);
        return ResponseEntity.noContent().build();
    }
}
