package cat.contacat.erp.core.partner.application;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.core.partner.PartnerAlreadyExistsException;
import cat.contacat.erp.core.partner.PartnerNotFoundException;
import cat.contacat.erp.core.partner.PartnerRepository;
import cat.contacat.erp.core.partner.PartnerValidationException;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PartnerApplicationService {

    private final PartnerRepository repository;
    private final CompanyRepository companyRepository;

    public PartnerApplicationService(PartnerRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<Partner> list(String companyId, String role) {
        ensureCompanyExists(companyId);
        return switch (normalizeRole(role)) {
            case "CUSTOMER" -> repository.findAllByCompanyIdAndCustomerTrueOrderByNameAsc(companyId);
            case "SUPPLIER" -> repository.findAllByCompanyIdAndSupplierTrueOrderByNameAsc(companyId);
            default -> repository.findAllByCompanyIdOrderByNameAsc(companyId);
        };
    }

    @Transactional(readOnly = true)
    public Partner get(String companyId, String partnerId) {
        return findPartner(companyId, partnerId);
    }

    @Transactional
    public Partner create(String companyId, PartnerCommand command) {
        Company company = findCompany(companyId);
        String normalizedTaxId = normalizeUpper(command.taxId());
        validateBusinessRules(command);
        ensureTaxIdAvailable(companyId, normalizedTaxId, null);

        Partner partner = new Partner();
        partner.setCompany(company);
        apply(partner, command, normalizedTaxId);
        return repository.save(partner);
    }

    @Transactional
    public Partner update(String companyId, String partnerId, PartnerCommand command) {
        Partner partner = findPartner(companyId, partnerId);
        String normalizedTaxId = normalizeUpper(command.taxId());
        validateBusinessRules(command);
        ensureTaxIdAvailable(companyId, normalizedTaxId, partnerId);

        apply(partner, command, normalizedTaxId);
        return repository.save(partner);
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
            .ifPresent(existing -> { throw new PartnerAlreadyExistsException(companyId, taxId); });
    }

    private void validateBusinessRules(PartnerCommand command) {
        if (!Boolean.TRUE.equals(command.isCustomer()) && !Boolean.TRUE.equals(command.isSupplier())) {
            throw new PartnerValidationException("El partner ha de ser client, proveidor o ambdos");
        }
        if (Boolean.TRUE.equals(command.isIntraEu()) && (command.euVatNumber() == null || command.euVatNumber().isBlank())) {
            throw new PartnerValidationException("El NIF intracomunitari es obligatori per a operadors intracomunitaris");
        }
        int paymentDays = command.paymentDays() == null ? 30 : command.paymentDays();
        if (paymentDays < 0) {
            throw new PartnerValidationException("Els dies de pagament no poden ser negatius");
        }
    }

    private void apply(Partner partner, PartnerCommand command, String normalizedTaxId) {
        partner.setName(command.name().trim());
        partner.setTaxId(normalizedTaxId);
        partner.setEmail(command.email().trim().toLowerCase(Locale.ROOT));
        partner.setPhone(command.phone().trim());
        partner.setCustomer(Boolean.TRUE.equals(command.isCustomer()));
        partner.setSupplier(Boolean.TRUE.equals(command.isSupplier()));
        partner.setDocumentType(normalizeUpperOrDefault(command.documentType(), "NIF"));
        partner.setAddressStreet(normalizeBlankToEmpty(command.addressStreet()));
        partner.setAddressNumber(normalizeBlankToEmpty(command.addressNumber()));
        partner.setAddressFloor(normalizeBlankToEmpty(command.addressFloor()));
        partner.setPostalCode(normalizeBlankToEmpty(command.postalCode()));
        partner.setCity(normalizeBlankToEmpty(command.city()));
        partner.setProvince(normalizeBlankToEmpty(command.province()));
        partner.setCountry(normalizeOrDefault(command.country(), "Espanya"));
        partner.setVatRegime(normalizeUpperOrDefault(command.vatRegime(), "GENERAL"));
        partner.setIntraEu(Boolean.TRUE.equals(command.isIntraEu()));
        partner.setEuVatNumber(normalizeUpperBlankToEmpty(command.euVatNumber()));
        partner.setIban(normalizeUpperBlankToEmpty(command.iban()));
        partner.setPaymentMethod(normalizeUpperOrDefault(command.paymentMethod(), "TRANSFER"));
        partner.setPaymentDays(command.paymentDays() == null ? 30 : command.paymentDays());
        partner.setActive(command.active() == null || command.active());
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
