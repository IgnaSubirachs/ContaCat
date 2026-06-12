package cat.contacat.erp.sales.order.api;

import cat.contacat.erp.sales.order.application.SalesOrderApplicationService;
import cat.contacat.erp.sales.order.application.SalesOrderCommand;
import cat.contacat.erp.sales.order.application.SalesOrderLineCommand;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/sales/companies/{companyId}/orders")
public class SalesOrderController {

    private final SalesOrderApplicationService service;

    public SalesOrderController(SalesOrderApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<SalesOrderResponse> list(@PathVariable String companyId, @RequestParam(required = false) String status) {
        return service.list(companyId, status).stream().map(SalesOrderResponse::from).toList();
    }

    @GetMapping("/{orderId}")
    public SalesOrderResponse get(@PathVariable String companyId, @PathVariable String orderId) {
        return SalesOrderResponse.from(service.get(companyId, orderId));
    }

    @PostMapping
    public ResponseEntity<SalesOrderResponse> create(@PathVariable String companyId, @Valid @RequestBody SalesOrderRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(SalesOrderResponse.from(service.create(companyId, toCommand(request))));
    }

    @PostMapping("/from-quote/{quoteId}")
    public ResponseEntity<SalesOrderResponse> createFromQuote(
        @PathVariable String companyId,
        @PathVariable String quoteId,
        @RequestBody(required = false) CreateOrderFromQuoteRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(SalesOrderResponse.from(service.createFromQuote(
            companyId,
            quoteId,
            request == null ? null : request.orderDate()
        )));
    }

    @PutMapping("/{orderId}")
    public SalesOrderResponse update(
        @PathVariable String companyId,
        @PathVariable String orderId,
        @Valid @RequestBody SalesOrderRequest request
    ) {
        return SalesOrderResponse.from(service.update(companyId, orderId, toCommand(request)));
    }

    @PostMapping("/{orderId}/confirm")
    public SalesOrderResponse confirm(@PathVariable String companyId, @PathVariable String orderId) {
        return SalesOrderResponse.from(service.confirm(companyId, orderId));
    }

    @PostMapping("/{orderId}/deliver")
    public SalesOrderResponse deliver(@PathVariable String companyId, @PathVariable String orderId) {
        return SalesOrderResponse.from(service.deliver(companyId, orderId));
    }

    @PostMapping("/{orderId}/cancel")
    public SalesOrderResponse cancel(@PathVariable String companyId, @PathVariable String orderId) {
        return SalesOrderResponse.from(service.cancel(companyId, orderId));
    }

    private SalesOrderCommand toCommand(SalesOrderRequest request) {
        return new SalesOrderCommand(
            request.partnerId(),
            request.series(),
            request.orderDate(),
            request.deliveryDate(),
            request.deliveryAddress(),
            request.notes(),
            request.lines().stream().map(line -> new SalesOrderLineCommand(
                line.productCode(),
                line.description(),
                line.quantity(),
                line.unitPrice(),
                line.discountPercent(),
                line.taxRate()
            )).toList()
        );
    }
}
