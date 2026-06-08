package cat.contacat.erp.core.company.application;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyAlreadyExistsException;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CompanyApplicationService {

    private final CompanyRepository repository;

    public CompanyApplicationService(CompanyRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    public List<Company> list() {
        return repository.findAll();
    }

    @Transactional(readOnly = true)
    public Company get(String id) {
        return findCompany(id);
    }

    @Transactional
    public Company create(CompanyCommand command) {
        ensureTaxIdAvailable(command.taxId(), null);

        Company company = new Company();
        apply(command, company);
        return repository.save(company);
    }

    @Transactional
    public Company update(String id, CompanyCommand command) {
        Company company = findCompany(id);
        ensureTaxIdAvailable(command.taxId(), id);

        apply(command, company);
        return repository.save(company);
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
            .ifPresent(existing -> { throw new CompanyAlreadyExistsException(existing.getTaxId()); });
    }

    private void apply(CompanyCommand command, Company company) {
        company.setName(command.name().trim());
        company.setLegalName(command.legalName().trim());
        company.setTaxId(command.taxId().trim().toUpperCase(Locale.ROOT));
        company.setCountry(normalizeOrDefault(command.country(), "ES"));
        company.setCurrency(normalizeOrDefault(command.currency(), "EUR"));
        company.setActive(command.active() == null || command.active());
    }

    private String normalizeOrDefault(String value, String defaultValue) {
        if (value == null || value.isBlank()) {
            return defaultValue;
        }
        return value.trim().toUpperCase(Locale.ROOT);
    }
}
