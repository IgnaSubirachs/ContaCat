package cat.contacat.erp.core.company;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.api.CompanyRequest;
import cat.contacat.erp.core.company.api.CompanyResponse;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class CompanyServiceTest {

    @Mock
    private CompanyRepository repository;

    @InjectMocks
    private CompanyService service;

    @Test
    void createNormalizesDefaultsAndPersistsCompany() {
        CompanyRequest request = new CompanyRequest(" ContaCat ", " ContaCat SL ", " b12345678 ", null, null, null);

        when(repository.findByTaxId("B12345678")).thenReturn(Optional.empty());
        when(repository.save(any(Company.class))).thenAnswer(invocation -> {
            Company company = invocation.getArgument(0);
            company.setId("company-1");
            return company;
        });

        CompanyResponse response = service.create(request);

        assertThat(response.id()).isEqualTo("company-1");
        assertThat(response.name()).isEqualTo("ContaCat");
        assertThat(response.legalName()).isEqualTo("ContaCat SL");
        assertThat(response.taxId()).isEqualTo("B12345678");
        assertThat(response.country()).isEqualTo("ES");
        assertThat(response.currency()).isEqualTo("EUR");
        assertThat(response.active()).isTrue();
    }

    @Test
    void createFailsWhenTaxIdAlreadyExists() {
        Company existing = new Company();
        existing.setId("existing-company");
        existing.setTaxId("B12345678");

        CompanyRequest request = new CompanyRequest("ContaCat", "ContaCat SL", "B12345678", "ES", "EUR", true);
        when(repository.findByTaxId("B12345678")).thenReturn(Optional.of(existing));

        assertThatThrownBy(() -> service.create(request))
            .isInstanceOf(CompanyAlreadyExistsException.class);
    }

    @Test
    void updateChangesCompanyFields() {
        Company company = new Company();
        company.setId("company-1");
        company.setName("Old");
        company.setLegalName("Old SL");
        company.setTaxId("B11111111");

        CompanyRequest request = new CompanyRequest("New", "New SL", "b22222222", "pt", "eur", false);
        when(repository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByTaxId("B22222222")).thenReturn(Optional.empty());
        when(repository.save(company)).thenReturn(company);

        CompanyResponse response = service.update("company-1", request);

        assertThat(response.name()).isEqualTo("New");
        assertThat(response.legalName()).isEqualTo("New SL");
        assertThat(response.taxId()).isEqualTo("B22222222");
        assertThat(response.country()).isEqualTo("PT");
        assertThat(response.currency()).isEqualTo("EUR");
        assertThat(response.active()).isFalse();
    }

    @Test
    void deactivateMarksCompanyAsInactive() {
        Company company = new Company();
        company.setId("company-1");
        company.setActive(true);

        when(repository.findById("company-1")).thenReturn(Optional.of(company));

        service.deactivate("company-1");

        assertThat(company.isActive()).isFalse();
        verify(repository).save(company);
    }
}
