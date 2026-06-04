package cat.contacat.erp.core.company;

import cat.contacat.erp.core.company.api.CompanyRequest;
import cat.contacat.erp.core.company.api.CompanyResponse;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CompanyService {

    private final CompanyRepository repository;

    public CompanyService(CompanyRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    public List<CompanyResponse> list() {
        return repository.findAll().stream()
            .map(CompanyResponse::from)
            .toList();
    }

    @Transactional(readOnly = true)
    public CompanyResponse get(String id) {
        return CompanyResponse.from(findCompany(id));
    }

    @Transactional
    public CompanyResponse create(CompanyRequest request) {
        ensureTaxIdAvailable(request.taxId(), null);

        Company company = new Company();
        apply(request, company);
        return CompanyResponse.from(repository.save(company));
    }

    @Transactional
    public CompanyResponse update(String id, CompanyRequest request) {
        Company company = findCompany(id);
        ensureTaxIdAvailable(request.taxId(), id);

        apply(request, company);
        return CompanyResponse.from(repository.save(company));
    }

    @Transactional
    public void deactivate(String id) {
        Company company = findCompany(id);
        company.setActive(false);
        repository.save(company);
    }

    private Company findCompany(String id) {
        return repository.findById(id)
            .orElseThrow(() -> new CompanyNotFoundException(id));
    }

    private void ensureTaxIdAvailable(String taxId, String currentCompanyId) {
        repository.findByTaxId(taxId.trim().toUpperCase(Locale.ROOT))
            .filter(existing -> !Objects.equals(existing.getId(), currentCompanyId))
            .ifPresent(existing -> {
                throw new CompanyAlreadyExistsException(existing.getTaxId());
            });
    }

    private void apply(CompanyRequest request, Company company) {
        company.setName(request.name().trim());
        company.setLegalName(request.legalName().trim());
        company.setTaxId(request.taxId().trim().toUpperCase(Locale.ROOT));
        company.setCountry(normalizeOrDefault(request.country(), "ES"));
        company.setCurrency(normalizeOrDefault(request.currency(), "EUR"));
        company.setActive(request.active() == null || request.active());
    }

    private String normalizeOrDefault(String value, String defaultValue) {
        if (value == null || value.isBlank()) {
            return defaultValue;
        }
        return value.trim().toUpperCase(Locale.ROOT);
    }
}
