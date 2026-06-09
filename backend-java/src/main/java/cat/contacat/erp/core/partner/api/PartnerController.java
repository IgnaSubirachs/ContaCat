package cat.contacat.erp.core.partner.api;

import cat.contacat.erp.core.partner.application.PartnerApplicationService;
import cat.contacat.erp.core.partner.application.PartnerCommand;
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
@RequestMapping("/api/core/companies/{companyId}/partners")
public class PartnerController {

    private final PartnerApplicationService service;

    public PartnerController(PartnerApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<PartnerResponse> list(
        @PathVariable String companyId,
        @RequestParam(required = false) String role
    ) {
        return service.list(companyId, role).stream().map(PartnerResponse::from).toList();
    }

    @GetMapping("/{partnerId}")
    public PartnerResponse get(@PathVariable String companyId, @PathVariable String partnerId) {
        return PartnerResponse.from(service.get(companyId, partnerId));
    }

    @PostMapping
    public ResponseEntity<PartnerResponse> create(
        @PathVariable String companyId,
        @Valid @RequestBody PartnerRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(PartnerResponse.from(service.create(companyId, toCommand(request))));
    }

    @PutMapping("/{partnerId}")
    public PartnerResponse update(
        @PathVariable String companyId,
        @PathVariable String partnerId,
        @Valid @RequestBody PartnerRequest request
    ) {
        return PartnerResponse.from(service.update(companyId, partnerId, toCommand(request)));
    }

    @DeleteMapping("/{partnerId}")
    public ResponseEntity<Void> deactivate(@PathVariable String companyId, @PathVariable String partnerId) {
        service.deactivate(companyId, partnerId);
        return ResponseEntity.noContent().build();
    }

    private PartnerCommand toCommand(PartnerRequest request) {
        return new PartnerCommand(
            request.name(),
            request.taxId(),
            request.email(),
            request.phone(),
            request.tradeName(),
            request.contactPerson(),
            request.mobile(),
            request.website(),
            request.customerCode(),
            request.supplierCode(),
            request.relationshipStatus(),
            request.relationshipSince(),
            request.salesRepresentative(),
            request.priceList(),
            request.defaultDiscount(),
            request.creditLimit(),
            request.paymentDay(),
            request.customerAccount(),
            request.supplierAccount(),
            request.bankName(),
            request.bankAccountHolder(),
            request.swiftBic(),
            request.contractSummary(),
            request.accrualNotes(),
            request.internalNotes(),
            request.isSupplier(),
            request.isCustomer(),
            request.documentType(),
            request.addressStreet(),
            request.addressNumber(),
            request.addressFloor(),
            request.postalCode(),
            request.city(),
            request.province(),
            request.country(),
            request.vatRegime(),
            request.isIntraEu(),
            request.euVatNumber(),
            request.iban(),
            request.paymentMethod(),
            request.paymentDays(),
            request.active()
        );
    }
}
