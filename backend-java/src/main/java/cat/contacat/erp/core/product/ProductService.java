package cat.contacat.erp.core.product;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.product.api.ProductRequest;
import cat.contacat.erp.core.product.api.ProductResponse;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProductService {

    private final ProductRepository repository;
    private final CompanyRepository companyRepository;

    public ProductService(ProductRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<ProductResponse> list(String companyId) {
        ensureCompanyExists(companyId);
        return repository.findAllByCompanyIdOrderBySkuAsc(companyId).stream()
            .map(ProductResponse::from)
            .toList();
    }

    @Transactional(readOnly = true)
    public ProductResponse get(String companyId, String productId) {
        return ProductResponse.from(findProduct(companyId, productId));
    }

    @Transactional
    public ProductResponse create(String companyId, ProductRequest request) {
        Company company = findCompany(companyId);
        String normalizedSku = normalizeUpper(request.sku());
        ensureSkuAvailable(companyId, normalizedSku, null);

        Product product = new Product();
        product.setCompany(company);
        apply(product, request, normalizedSku);
        return ProductResponse.from(repository.save(product));
    }

    @Transactional
    public ProductResponse update(String companyId, String productId, ProductRequest request) {
        Product product = findProduct(companyId, productId);
        String normalizedSku = normalizeUpper(request.sku());
        ensureSkuAvailable(companyId, normalizedSku, productId);

        apply(product, request, normalizedSku);
        return ProductResponse.from(repository.save(product));
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
            .ifPresent(existing -> {
                throw new ProductAlreadyExistsException(companyId, sku);
            });
    }

    private void apply(Product product, ProductRequest request, String normalizedSku) {
        product.setSku(normalizedSku);
        product.setName(request.name().trim());
        product.setDescription(normalizeNullable(request.description()));
        product.setProductType(normalizeUpperOrDefault(request.productType(), "GOOD"));
        product.setDefaultTaxCode(normalizeUpperNullable(request.defaultTaxCode()));
        product.setSalesAccountCode(normalizeNullable(request.salesAccountCode()));
        product.setPurchaseAccountCode(normalizeNullable(request.purchaseAccountCode()));
        product.setActive(request.active() == null || request.active());
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
