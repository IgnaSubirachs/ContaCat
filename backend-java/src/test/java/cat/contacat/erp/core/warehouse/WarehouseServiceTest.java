package cat.contacat.erp.core.warehouse;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.warehouse.api.WarehouseRequest;
import cat.contacat.erp.core.warehouse.api.WarehouseResponse;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class WarehouseServiceTest {

    @Mock
    private WarehouseRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private WarehouseService service;

    @Test
    void createNormalizesCodeAndPersistsWarehouse() {
        Company company = new Company();
        company.setId("company-1");

        WarehouseRequest request = new WarehouseRequest(" bcn ", " Central Barcelona ", null);

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByCompanyIdAndCode("company-1", "BCN")).thenReturn(Optional.empty());
        when(repository.save(any(Warehouse.class))).thenAnswer(invocation -> {
            Warehouse warehouse = invocation.getArgument(0);
            warehouse.setId("warehouse-1");
            return warehouse;
        });

        WarehouseResponse response = service.create("company-1", request);

        assertThat(response.id()).isEqualTo("warehouse-1");
        assertThat(response.companyId()).isEqualTo("company-1");
        assertThat(response.code()).isEqualTo("BCN");
        assertThat(response.name()).isEqualTo("Central Barcelona");
        assertThat(response.active()).isTrue();
    }

    @Test
    void createFailsWhenCodeAlreadyExistsInCompany() {
        Company company = new Company();
        company.setId("company-1");

        Warehouse existing = new Warehouse();
        existing.setId("warehouse-1");
        existing.setCompany(company);
        existing.setCode("BCN");

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByCompanyIdAndCode("company-1", "BCN")).thenReturn(Optional.of(existing));

        assertThatThrownBy(() -> service.create("company-1", new WarehouseRequest("BCN", "Magatzem", true)))
            .isInstanceOf(WarehouseAlreadyExistsException.class);
    }

    @Test
    void deactivateMarksWarehouseAsInactive() {
        Company company = new Company();
        company.setId("company-1");

        Warehouse warehouse = new Warehouse();
        warehouse.setId("warehouse-1");
        warehouse.setCompany(company);
        warehouse.setActive(true);

        when(repository.findById("warehouse-1")).thenReturn(Optional.of(warehouse));

        service.deactivate("company-1", "warehouse-1");

        assertThat(warehouse.isActive()).isFalse();
        verify(repository).save(warehouse);
    }
}
