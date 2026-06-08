package cat.contacat.erp.core.tax.application;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.tax.TaxRate;
import cat.contacat.erp.core.tax.TaxRateAlreadyExistsException;
import cat.contacat.erp.core.tax.TaxRateNotFoundException;
import cat.contacat.erp.core.tax.TaxRateRepository;
import java.math.RoundingMode;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TaxRateApplicationService {

    private final TaxRateRepository repository;
    private final CompanyRepository companyRepository;

    public TaxRateApplicationService(TaxRateRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<TaxRate> list(String companyId) {
        ensureCompanyExists(companyId);
        return repository.findAllByCompanyIdOrderByCodeAsc(companyId);
    }

    @Transactional(readOnly = true)
    public TaxRate get(String companyId, String taxRateId) {
        return findTaxRate(companyId, taxRateId);
    }

    @Transactional
    public TaxRate create(String companyId, TaxRateCommand command) {
        Company company = findCompany(companyId);
        String normalizedCode = normalizeUpper(command.code());
        ensureCodeAvailable(companyId, normalizedCode, null);

        TaxRate taxRate = new TaxRate();
        taxRate.setCompany(company);
        apply(taxRate, command, normalizedCode);
        return repository.save(taxRate);
    }

    @Transactional
    public TaxRate update(String companyId, String taxRateId, TaxRateCommand command) {
        TaxRate taxRate = findTaxRate(companyId, taxRateId);
        String normalizedCode = normalizeUpper(command.code());
        ensureCodeAvailable(companyId, normalizedCode, taxRateId);

        apply(taxRate, command, normalizedCode);
        return repository.save(taxRate);
    }

    @Transactional
    public void deactivate(String companyId, String taxRateId) {
        TaxRate taxRate = findTaxRate(companyId, taxRateId);
        taxRate.setActive(false);
        repository.save(taxRate);
    }

    private TaxRate findTaxRate(String companyId, String taxRateId) {
        TaxRate taxRate = repository.findById(taxRateId)
            .orElseThrow(() -> new TaxRateNotFoundException(companyId, taxRateId));

        if (!Objects.equals(taxRate.getCompany().getId(), companyId)) {
            throw new TaxRateNotFoundException(companyId, taxRateId);
        }
        return taxRate;
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

    private void ensureCodeAvailable(String companyId, String code, String currentTaxRateId) {
        repository.findByCompanyIdAndCode(companyId, code)
            .filter(existing -> !Objects.equals(existing.getId(), currentTaxRateId))
            .ifPresent(existing -> { throw new TaxRateAlreadyExistsException(companyId, code); });
    }

    private void apply(TaxRate taxRate, TaxRateCommand command, String normalizedCode) {
        taxRate.setCode(normalizedCode);
        taxRate.setName(command.name().trim());
        taxRate.setRate(command.rate().setScale(2, RoundingMode.HALF_UP));
        taxRate.setTaxType(normalizeUpperOrDefault(command.taxType(), "VAT"));
        taxRate.setInputAccountCode(normalizeNullable(command.inputAccountCode()));
        taxRate.setOutputAccountCode(normalizeNullable(command.outputAccountCode()));
        taxRate.setActive(command.active() == null || command.active());
    }

    private String normalizeUpper(String value) {
        return value.trim().toUpperCase(Locale.ROOT);
    }

    private String normalizeUpperOrDefault(String value, String defaultValue) {
        return value == null || value.isBlank()
            ? defaultValue
            : value.trim().toUpperCase(Locale.ROOT);
    }

    private String normalizeNullable(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return value.trim();
    }
}
