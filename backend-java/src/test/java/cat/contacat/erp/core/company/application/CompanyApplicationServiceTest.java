package cat.contacat.erp.core.company.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyAlreadyExistsException;
import cat.contacat.erp.core.company.CompanyRepository;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class CompanyApplicationServiceTest {

    @Mock
    private CompanyRepository repository;

    @InjectMocks
    private CompanyApplicationService service;

    @Test
    void createNormalizesDefaultsAndPersistsCompany() {
        CompanyCommand command = new CompanyCommand(" ContaCat ", " ContaCat SL ", " b12345678 ", null, null, null);

        when(repository.findByTaxId("B12345678")).thenReturn(Optional.empty());
        when(repository.save(any(Company.class))).thenAnswer(invocation -> {
            Company company = invocation.getArgument(0);
            company.setId("company-1");
            return company;
        });

        Company company = service.create(command);

        assertThat(company.getId()).isEqualTo("company-1");
        assertThat(company.getName()).isEqualTo("ContaCat");
        assertThat(company.getLegalName()).isEqualTo("ContaCat SL");
        assertThat(company.getTaxId()).isEqualTo("B12345678");
        assertThat(company.getCountry()).isEqualTo("ES");
        assertThat(company.getCurrency()).isEqualTo("EUR");
        assertThat(company.isActive()).isTrue();
    }

    @Test
    void createFailsWhenTaxIdAlreadyExists() {
        Company existing = new Company();
        existing.setId("existing-company");
        existing.setTaxId("B12345678");

        CompanyCommand command = new CompanyCommand("ContaCat", "ContaCat SL", "B12345678", "ES", "EUR", true);
        when(repository.findByTaxId("B12345678")).thenReturn(Optional.of(existing));

        assertThatThrownBy(() -> service.create(command))
            .isInstanceOf(CompanyAlreadyExistsException.class);
    }

    @Test
    void updateChangesCompanyFields() {
        Company company = new Company();
        company.setId("company-1");
        company.setName("Old");
        company.setLegalName("Old SL");
        company.setTaxId("B11111111");

        CompanyCommand command = new CompanyCommand("New", "New SL", "b22222222", "pt", "eur", false);
        when(repository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByTaxId("B22222222")).thenReturn(Optional.empty());
        when(repository.save(company)).thenReturn(company);

        Company response = service.update("company-1", command);

        assertThat(response.getName()).isEqualTo("New");
        assertThat(response.getLegalName()).isEqualTo("New SL");
        assertThat(response.getTaxId()).isEqualTo("B22222222");
        assertThat(response.getCountry()).isEqualTo("PT");
        assertThat(response.getCurrency()).isEqualTo("EUR");
        assertThat(response.isActive()).isFalse();
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
