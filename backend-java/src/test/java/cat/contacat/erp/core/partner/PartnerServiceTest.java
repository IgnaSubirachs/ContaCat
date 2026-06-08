package cat.contacat.erp.core.partner;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.partner.api.PartnerRequest;
import cat.contacat.erp.core.partner.api.PartnerResponse;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class PartnerServiceTest {

    @Mock
    private PartnerRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private PartnerService service;

    @Test
    void createNormalizesAndPersistsPartner() {
        Company company = new Company();
        company.setId("company-1");

        PartnerRequest request = new PartnerRequest(
            " Client Demo ",
            " b12345678 ",
            "FACTURES@CLIENT.CAT",
            " 931000000 ",
            false,
            true,
            null,
            "Carrer Major",
            "12",
            "1r",
            "08001",
            "Barcelona",
            "Barcelona",
            null,
            null,
            false,
            null,
            " es9121000418450200051332 ",
            null,
            30,
            null
        );

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.save(any(Partner.class))).thenAnswer(invocation -> {
            Partner partner = invocation.getArgument(0);
            partner.setId("partner-1");
            return partner;
        });

        PartnerResponse response = service.create("company-1", request);

        assertThat(response.id()).isEqualTo("partner-1");
        assertThat(response.companyId()).isEqualTo("company-1");
        assertThat(response.taxId()).isEqualTo("B12345678");
        assertThat(response.email()).isEqualTo("factures@client.cat");
        assertThat(response.customer()).isTrue();
        assertThat(response.supplier()).isFalse();
        assertThat(response.country()).isEqualTo("Espanya");
        assertThat(response.iban()).isEqualTo("ES9121000418450200051332");
        assertThat(response.paymentMethod()).isEqualTo("TRANSFER");
        assertThat(response.active()).isTrue();
    }

    @Test
    void createFailsWhenTaxIdAlreadyExistsInCompany() {
        Company company = new Company();
        company.setId("company-1");

        Partner existing = new Partner();
        existing.setId("partner-1");
        existing.setCompany(company);
        existing.setTaxId("B12345678");

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByCompanyIdAndTaxId("company-1", "B12345678")).thenReturn(Optional.of(existing));

        PartnerRequest request = validRequest();

        assertThatThrownBy(() -> service.create("company-1", request))
            .isInstanceOf(PartnerAlreadyExistsException.class);
    }

    @Test
    void createFailsWhenPartnerHasNoRole() {
        Company company = new Company();
        company.setId("company-1");

        PartnerRequest request = new PartnerRequest(
            "Partner",
            "B12345678",
            "mail@test.cat",
            "931000000",
            false,
            false,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            false,
            null,
            null,
            null,
            30,
            true
        );

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));

        assertThatThrownBy(() -> service.create("company-1", request))
            .isInstanceOf(PartnerValidationException.class)
            .hasMessageContaining("client");
    }

    @Test
    void listFiltersCustomersWhenRoleRequested() {
        when(companyRepository.existsById("company-1")).thenReturn(true);

        Company company = new Company();
        company.setId("company-1");

        Partner partner = new Partner();
        partner.setId("partner-1");
        partner.setCompany(company);
        partner.setName("Client 1");
        partner.setTaxId("B12345678");
        partner.setEmail("client@test.cat");
        partner.setPhone("931000000");
        partner.setCustomer(true);

        when(repository.findAllByCompanyIdAndCustomerTrueOrderByNameAsc("company-1")).thenReturn(List.of(partner));

        List<PartnerResponse> response = service.list("company-1", "customer");

        assertThat(response).hasSize(1);
        assertThat(response.get(0).customer()).isTrue();
    }

    @Test
    void deactivateMarksPartnerAsInactive() {
        Company company = new Company();
        company.setId("company-1");

        Partner partner = new Partner();
        partner.setId("partner-1");
        partner.setCompany(company);
        partner.setActive(true);

        when(repository.findById("partner-1")).thenReturn(Optional.of(partner));

        service.deactivate("company-1", "partner-1");

        assertThat(partner.isActive()).isFalse();
        verify(repository).save(partner);
    }

    private PartnerRequest validRequest() {
        return new PartnerRequest(
            "Partner",
            "B12345678",
            "mail@test.cat",
            "931000000",
            true,
            false,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            false,
            null,
            null,
            null,
            30,
            true
        );
    }
}
