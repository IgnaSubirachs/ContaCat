package cat.contacat.erp.core.tax;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.tax.api.TaxRateRequest;
import cat.contacat.erp.core.tax.api.TaxRateResponse;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TaxRateService {

    private final TaxRateRepository repository;
    private final CompanyRepository companyRepository;

    public TaxRateService(TaxRateRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<TaxRateResponse> list(String companyId) {
        ensureCompanyExists(companyId);
        return repository.findAllByCompanyIdOrderByCodeAsc(companyId).stream()
            .map(TaxRateResponse::from)
            .toList();
    }

    @Transactional(readOnly = true)
    public TaxRateResponse get(String companyId, String taxRateId) {
        return TaxRateResponse.from(findTaxRate(companyId, taxRateId));
    }

    @Transactional
    public TaxRateResponse create(String companyId, TaxRateRequest request) {
        Company company = findCompany(companyId);
        String normalizedCode = normalizeUpper(request.code());
        ensureCodeAvailable(companyId, normalizedCode, null);

        TaxRate taxRate = new TaxRate();
        taxRate.setCompany(company);
        apply(taxRate, request, normalizedCode);
        return TaxRateResponse.from(repository.save(taxRate));
    }

    @Transactional
    public TaxRateResponse update(String companyId, String taxRateId, TaxRateRequest request) {
        TaxRate taxRate = findTaxRate(companyId, taxRateId);
        String normalizedCode = normalizeUpper(request.code());
        ensureCodeAvailable(companyId, normalizedCode, taxRateId);

        apply(taxRate, request, normalizedCode);
        return TaxRateResponse.from(repository.save(taxRate));
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
            .ifPresent(existing -> {
                throw new TaxRateAlreadyExistsException(companyId, code);
            });
    }

    private void apply(TaxRate taxRate, TaxRateRequest request, String normalizedCode) {
        taxRate.setCode(normalizedCode);
        taxRate.setName(request.name().trim());
        taxRate.setRate(request.rate().setScale(2, RoundingMode.HALF_UP));
        taxRate.setTaxType(normalizeUpperOrDefault(request.taxType(), "VAT"));
        taxRate.setInputAccountCode(normalizeNullable(request.inputAccountCode()));
        taxRate.setOutputAccountCode(normalizeNullable(request.outputAccountCode()));
        taxRate.setActive(request.active() == null || request.active());
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
