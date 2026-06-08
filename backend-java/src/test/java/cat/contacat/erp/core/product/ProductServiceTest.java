package cat.contacat.erp.core.product;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.product.api.ProductRequest;
import cat.contacat.erp.core.product.api.ProductResponse;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock
    private ProductRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private ProductService service;

    @Test
    void createNormalizesSkuAndPersistsProduct() {
        Company company = new Company();
        company.setId("company-1");

        ProductRequest request = new ProductRequest(
            " sku-001 ",
            " Teclat mecànic ",
            " Oficina ",
            " service ",
            " iva21 ",
            " 700000 ",
            " 600000 ",
            null
        );

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByCompanyIdAndSku("company-1", "SKU-001")).thenReturn(Optional.empty());
        when(repository.save(any(Product.class))).thenAnswer(invocation -> {
            Product product = invocation.getArgument(0);
            product.setId("product-1");
            return product;
        });

        ProductResponse response = service.create("company-1", request);

        assertThat(response.id()).isEqualTo("product-1");
        assertThat(response.companyId()).isEqualTo("company-1");
        assertThat(response.sku()).isEqualTo("SKU-001");
        assertThat(response.name()).isEqualTo("Teclat mecànic");
        assertThat(response.productType()).isEqualTo("SERVICE");
        assertThat(response.defaultTaxCode()).isEqualTo("IVA21");
        assertThat(response.salesAccountCode()).isEqualTo("700000");
        assertThat(response.purchaseAccountCode()).isEqualTo("600000");
        assertThat(response.active()).isTrue();
    }

    @Test
    void createFailsWhenSkuAlreadyExistsInCompany() {
        Company existingCompany = new Company();
        existingCompany.setId("company-1");

        Product existing = new Product();
        existing.setId("product-1");
        existing.setCompany(existingCompany);
        existing.setSku("SKU-001");

        ProductRequest request = new ProductRequest("SKU-001", "Producte", null, null, null, null, null, true);

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(existingCompany));
        when(repository.findByCompanyIdAndSku("company-1", "SKU-001")).thenReturn(Optional.of(existing));

        assertThatThrownBy(() -> service.create("company-1", request))
            .isInstanceOf(ProductAlreadyExistsException.class);
    }

    @Test
    void deactivateMarksProductAsInactive() {
        Company company = new Company();
        company.setId("company-1");

        Product product = new Product();
        product.setId("product-1");
        product.setCompany(company);
        product.setActive(true);

        when(repository.findById("product-1")).thenReturn(Optional.of(product));

        service.deactivate("company-1", "product-1");

        assertThat(product.isActive()).isFalse();
        verify(repository).save(product);
    }
}
