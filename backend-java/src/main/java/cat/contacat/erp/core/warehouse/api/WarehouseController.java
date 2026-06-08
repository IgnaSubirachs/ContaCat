package cat.contacat.erp.core.warehouse.api;

import cat.contacat.erp.core.warehouse.application.WarehouseApplicationService;
import cat.contacat.erp.core.warehouse.application.WarehouseCommand;
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
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/core/companies/{companyId}/warehouses")
public class WarehouseController {

    private final WarehouseApplicationService service;

    public WarehouseController(WarehouseApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<WarehouseResponse> list(@PathVariable String companyId) {
        return service.list(companyId).stream().map(WarehouseResponse::from).toList();
    }

    @GetMapping("/{warehouseId}")
    public WarehouseResponse get(@PathVariable String companyId, @PathVariable String warehouseId) {
        return WarehouseResponse.from(service.get(companyId, warehouseId));
    }

    @PostMapping
    public ResponseEntity<WarehouseResponse> create(
        @PathVariable String companyId,
        @Valid @RequestBody WarehouseRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(WarehouseResponse.from(service.create(companyId, toCommand(request))));
    }

    @PutMapping("/{warehouseId}")
    public WarehouseResponse update(
        @PathVariable String companyId,
        @PathVariable String warehouseId,
        @Valid @RequestBody WarehouseRequest request
    ) {
        return WarehouseResponse.from(service.update(companyId, warehouseId, toCommand(request)));
    }

    @DeleteMapping("/{warehouseId}")
    public ResponseEntity<Void> deactivate(@PathVariable String companyId, @PathVariable String warehouseId) {
        service.deactivate(companyId, warehouseId);
        return ResponseEntity.noContent().build();
    }

    private WarehouseCommand toCommand(WarehouseRequest request) {
        return new WarehouseCommand(request.code(), request.name(), request.active());
    }
}
