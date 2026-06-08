package cat.contacat.erp.core.product.application;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.product.Product;
import cat.contacat.erp.core.product.ProductAlreadyExistsException;
import cat.contacat.erp.core.product.ProductNotFoundException;
import cat.contacat.erp.core.product.ProductRepository;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProductApplicationService {

    private final ProductRepository repository;
    private final CompanyRepository companyRepository;

    public ProductApplicationService(ProductRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<Product> list(String companyId) {
        ensureCompanyExists(companyId);
        return repository.findAllByCompanyIdOrderBySkuAsc(companyId);
    }

    @Transactional(readOnly = true)
    public Product get(String companyId, String productId) {
        return findProduct(companyId, productId);
    }

    @Transactional
    public Product create(String companyId, ProductCommand command) {
        Company company = findCompany(companyId);
        String normalizedSku = normalizeUpper(command.sku());
        ensureSkuAvailable(companyId, normalizedSku, null);

        Product product = new Product();
        product.setCompany(company);
        apply(product, command, normalizedSku);
        return repository.save(product);
    }

    @Transactional
    public Product update(String companyId, String productId, ProductCommand command) {
        Product product = findProduct(companyId, productId);
        String normalizedSku = normalizeUpper(command.sku());
        ensureSkuAvailable(companyId, normalizedSku, productId);

        apply(product, command, normalizedSku);
        return repository.save(product);
    }

    @Transactional
    public void deactivate(String companyId, String productId) {
        Product product = findProduct(companyId, productId);
        product.setActive(false);
        repository.save(product);
    }

    private Product findProduct(String companyId, String productId) {
        Product product = repository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(companyId, productId));

        if (!Objects.equals(product.getCompany().getId(), companyId)) {
            throw new ProductNotFoundException(companyId, productId);
        }
        return product;
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

    private void ensureSkuAvailable(String companyId, String sku, String currentProductId) {
        repository.findByCompanyIdAndSku(companyId, sku)
            .filter(existing -> !Objects.equals(existing.getId(), currentProductId))
            .ifPresent(existing -> { throw new ProductAlreadyExistsException(companyId, sku); });
    }

    private void apply(Product product, ProductCommand command, String normalizedSku) {
        product.setSku(normalizedSku);
        product.setName(command.name().trim());
        product.setDescription(normalizeNullable(command.description()));
        product.setProductType(normalizeUpperOrDefault(command.productType(), "GOOD"));
        product.setDefaultTaxCode(normalizeUpperNullable(command.defaultTaxCode()));
        product.setSalesAccountCode(normalizeNullable(command.salesAccountCode()));
        product.setPurchaseAccountCode(normalizeNullable(command.purchaseAccountCode()));
        product.setActive(command.active() == null || command.active());
    }

    private String normalizeUpper(String value) {
        return value.trim().toUpperCase(Locale.ROOT);
    }

    private String normalizeUpperNullable(String value) {
        String normalized = normalizeNullable(value);
        return normalized == null ? null : normalized.toUpperCase(Locale.ROOT);
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
