package cat.contacat.erp.core.partner;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.partner.api.PartnerRequest;
import cat.contacat.erp.core.partner.api.PartnerResponse;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PartnerService {

    private final PartnerRepository repository;
    private final CompanyRepository companyRepository;

    public PartnerService(PartnerRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<PartnerResponse> list(String companyId, String role) {
        ensureCompanyExists(companyId);
        List<Partner> partners = switch (normalizeRole(role)) {
            case "CUSTOMER" -> repository.findAllByCompanyIdAndCustomerTrueOrderByNameAsc(companyId);
            case "SUPPLIER" -> repository.findAllByCompanyIdAndSupplierTrueOrderByNameAsc(companyId);
            default -> repository.findAllByCompanyIdOrderByNameAsc(companyId);
        };
        return partners.stream().map(PartnerResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public PartnerResponse get(String companyId, String partnerId) {
        return PartnerResponse.from(findPartner(companyId, partnerId));
    }

    @Transactional
    public PartnerResponse create(String companyId, PartnerRequest request) {
        Company company = findCompany(companyId);
        String normalizedTaxId = normalizeUpper(request.taxId());
        validateBusinessRules(request);
        ensureTaxIdAvailable(companyId, normalizedTaxId, null);

        Partner partner = new Partner();
        partner.setCompany(company);
        apply(partner, request, normalizedTaxId);
        return PartnerResponse.from(repository.save(partner));
    }

    @Transactional
    public PartnerResponse update(String companyId, String partnerId, PartnerRequest request) {
        Partner partner = findPartner(companyId, partnerId);
        String normalizedTaxId = normalizeUpper(request.taxId());
        validateBusinessRules(request);
        ensureTaxIdAvailable(companyId, normalizedTaxId, partnerId);

        apply(partner, request, normalizedTaxId);
        return PartnerResponse.from(repository.save(partner));
    }

    @Transactional
    public void deactivate(String companyId, String partnerId) {
        Partner partner = findPartner(companyId, partnerId);
        partner.setActive(false);
        repository.save(partner);
    }

    private Partner findPartner(String companyId, String partnerId) {
        Partner partner = repository.findById(partnerId)
            .orElseThrow(() -> new PartnerNotFoundException(companyId, partnerId));

        if (!Objects.equals(partner.getCompany().getId(), companyId)) {
            throw new PartnerNotFoundException(companyId, partnerId);
        }
        return partner;
    }

    private Company findCompany(String companyId) {
        return companyRepository.findById(companyId)
            .orElseThrow(() -> new CompanyNotFoundException(companyId));
    }

    private void ensureCompanyExists(String companyId) {
        if (!companyRepository.existsById(companyId)) {
            throw new CompanyNotFoundException(companyId);
        }
    }

    private void ensureTaxIdAvailable(String companyId, String taxId, String currentPartnerId) {
        repository.findByCompanyIdAndTaxId(companyId, taxId)
            .filter(existing -> !Objects.equals(existing.getId(), currentPartnerId))
            .ifPresent(existing -> {
                throw new PartnerAlreadyExistsException(companyId, taxId);
            });
    }

    private void validateBusinessRules(PartnerRequest request) {
        if (!request.isCustomer() && !request.isSupplier()) {
            throw new PartnerValidationException("El partner ha de ser client, proveidor o ambdos");
        }
        if (Boolean.TRUE.equals(request.isIntraEu()) && (request.euVatNumber() == null || request.euVatNumber().isBlank())) {
            throw new PartnerValidationException("El NIF intracomunitari es obligatori per a operadors intracomunitaris");
        }
        int paymentDays = request.paymentDays() == null ? 30 : request.paymentDays();
        if (paymentDays < 0) {
            throw new PartnerValidationException("Els dies de pagament no poden ser negatius");
        }
    }

    private void apply(Partner partner, PartnerRequest request, String normalizedTaxId) {
        partner.setName(request.name().trim());
        partner.setTaxId(normalizedTaxId);
        partner.setEmail(request.email().trim().toLowerCase(Locale.ROOT));
        partner.setPhone(request.phone().trim());
        partner.setCustomer(request.isCustomer());
        partner.setSupplier(request.isSupplier());
        partner.setDocumentType(normalizeUpperOrDefault(request.documentType(), "NIF"));
        partner.setAddressStreet(normalizeBlankToEmpty(request.addressStreet()));
        partner.setAddressNumber(normalizeBlankToEmpty(request.addressNumber()));
        partner.setAddressFloor(normalizeBlankToEmpty(request.addressFloor()));
        partner.setPostalCode(normalizeBlankToEmpty(request.postalCode()));
        partner.setCity(normalizeBlankToEmpty(request.city()));
        partner.setProvince(normalizeBlankToEmpty(request.province()));
        partner.setCountry(normalizeOrDefault(request.country(), "Espanya"));
        partner.setVatRegime(normalizeUpperOrDefault(request.vatRegime(), "GENERAL"));
        partner.setIntraEu(Boolean.TRUE.equals(request.isIntraEu()));
        partner.setEuVatNumber(normalizeUpperBlankToEmpty(request.euVatNumber()));
        partner.setIban(normalizeUpperBlankToEmpty(request.iban()));
        partner.setPaymentMethod(normalizeUpperOrDefault(request.paymentMethod(), "TRANSFER"));
        partner.setPaymentDays(request.paymentDays() == null ? 30 : request.paymentDays());
        partner.setActive(request.active() == null || request.active());
    }

    private String normalizeRole(String role) {
        if (role == null || role.isBlank()) {
            return "ALL";
        }
        String normalized = role.trim().toUpperCase(Locale.ROOT);
        if (!normalized.equals("CUSTOMER") && !normalized.equals("SUPPLIER") && !normalized.equals("ALL")) {
            throw new PartnerValidationException("El filtre role ha de ser ALL, CUSTOMER o SUPPLIER");
        }
        return normalized;
    }

    private String normalizeUpper(String value) {
        return value.trim().toUpperCase(Locale.ROOT);
    }

    private String normalizeUpperBlankToEmpty(String value) {
        return value == null || value.isBlank() ? "" : value.trim().toUpperCase(Locale.ROOT);
    }

    private String normalizeUpperOrDefault(String value, String defaultValue) {
        return value == null || value.isBlank()
            ? defaultValue
            : value.trim().toUpperCase(Locale.ROOT);
    }

    private String normalizeOrDefault(String value, String defaultValue) {
        return value == null || value.isBlank() ? defaultValue : value.trim();
    }

    private String normalizeBlankToEmpty(String value) {
        return value == null || value.isBlank() ? "" : value.trim();
    }
}
