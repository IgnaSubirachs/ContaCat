package cat.contacat.erp.core.product.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.product.Product;
import cat.contacat.erp.core.product.ProductAlreadyExistsException;
import cat.contacat.erp.core.product.ProductRepository;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ProductApplicationServiceTest {

    @Mock
    private ProductRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private ProductApplicationService service;

    @Test
    void createNormalizesSkuAndPersistsProduct() {
        Company company = new Company();
        company.setId("company-1");

        ProductCommand command = new ProductCommand(
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

        Product product = service.create("company-1", command);

        assertThat(product.getId()).isEqualTo("product-1");
        assertThat(product.getSku()).isEqualTo("SKU-001");
        assertThat(product.getName()).isEqualTo("Teclat mecànic");
        assertThat(product.getProductType()).isEqualTo("SERVICE");
        assertThat(product.getDefaultTaxCode()).isEqualTo("IVA21");
        assertThat(product.getSalesAccountCode()).isEqualTo("700000");
        assertThat(product.getPurchaseAccountCode()).isEqualTo("600000");
        assertThat(product.isActive()).isTrue();
    }

    @Test
    void createFailsWhenSkuAlreadyExistsInCompany() {
        Company existingCompany = new Company();
        existingCompany.setId("company-1");

        Product existing = new Product();
        existing.setId("product-1");
        existing.setCompany(existingCompany);
        existing.setSku("SKU-001");

        ProductCommand command = new ProductCommand("SKU-001", "Producte", null, null, null, null, null, true);

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(existingCompany));
        when(repository.findByCompanyIdAndSku("company-1", "SKU-001")).thenReturn(Optional.of(existing));

        assertThatThrownBy(() -> service.create("company-1", command))
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
