package cat.contacat.erp.core.partner.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.core.partner.PartnerAlreadyExistsException;
import cat.contacat.erp.core.partner.PartnerRepository;
import cat.contacat.erp.core.partner.PartnerValidationException;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class PartnerApplicationServiceTest {

    @Mock
    private PartnerRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private PartnerApplicationService service;

    @Test
    void createNormalizesAndPersistsPartner() {
        Company company = new Company();
        company.setId("company-1");

        PartnerCommand command = new PartnerCommand(
            " Client Demo ",
            " b12345678 ",
            "FACTURES@CLIENT.CAT",
            " 931000000 ",
            " Client Demo Comercial ",
            " Marta Serra ",
            " 600111222 ",
            " https://client.cat ",
            " C-100 ",
            " S-100 ",
            "active",
            LocalDate.of(2026, 1, 1),
            " Carla Clos ",
            " Premium ",
            new BigDecimal("5.50"),
            new BigDecimal("12000.00"),
            15,
            " 430000 ",
            " 400000 ",
            " CaixaBank ",
            " Client Demo SL ",
            " bbaresmmxxx ",
            " Contracte anual ",
            " Periodificacio mensual ",
            " Nota interna ",
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

        Partner partner = service.create("company-1", command);

        assertThat(partner.getId()).isEqualTo("partner-1");
        assertThat(partner.getTaxId()).isEqualTo("B12345678");
        assertThat(partner.getEmail()).isEqualTo("factures@client.cat");
        assertThat(partner.getTradeName()).isEqualTo("Client Demo Comercial");
        assertThat(partner.getRelationshipStatus()).isEqualTo("ACTIVE");
        assertThat(partner.getDefaultDiscount()).isEqualByComparingTo("5.50");
        assertThat(partner.getCreditLimit()).isEqualByComparingTo("12000.00");
        assertThat(partner.getPaymentDay()).isEqualTo(15);
        assertThat(partner.getCustomerAccount()).isEqualTo("430000");
        assertThat(partner.getSupplierAccount()).isEqualTo("400000");
        assertThat(partner.getSwiftBic()).isEqualTo("BBARESMMXXX");
        assertThat(partner.getCountry()).isEqualTo("Espanya");
        assertThat(partner.getIban()).isEqualTo("ES9121000418450200051332");
        assertThat(partner.getPaymentMethod()).isEqualTo("TRANSFER");
        assertThat(partner.isActive()).isTrue();
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

        PartnerCommand command = validCommand();

        assertThatThrownBy(() -> service.create("company-1", command))
            .isInstanceOf(PartnerAlreadyExistsException.class);
    }

    @Test
    void createFailsWhenPartnerHasNoRole() {
        Company company = new Company();
        company.setId("company-1");

        PartnerCommand command = commandWithRoles(false, false);

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));

        assertThatThrownBy(() -> service.create("company-1", command))
            .isInstanceOf(PartnerValidationException.class)
            .hasMessageContaining("client");
    }

    @Test
    void createFailsWhenPaymentDayIsOutOfRange() {
        Company company = new Company();
        company.setId("company-1");

        PartnerCommand command = new PartnerCommand(
            validCommand().name(),
            validCommand().taxId(),
            validCommand().email(),
            validCommand().phone(),
            validCommand().tradeName(),
            validCommand().contactPerson(),
            validCommand().mobile(),
            validCommand().website(),
            validCommand().customerCode(),
            validCommand().supplierCode(),
            validCommand().relationshipStatus(),
            validCommand().relationshipSince(),
            validCommand().salesRepresentative(),
            validCommand().priceList(),
            validCommand().defaultDiscount(),
            validCommand().creditLimit(),
            35,
            validCommand().customerAccount(),
            validCommand().supplierAccount(),
            validCommand().bankName(),
            validCommand().bankAccountHolder(),
            validCommand().swiftBic(),
            validCommand().contractSummary(),
            validCommand().accrualNotes(),
            validCommand().internalNotes(),
            validCommand().isSupplier(),
            validCommand().isCustomer(),
            validCommand().documentType(),
            validCommand().addressStreet(),
            validCommand().addressNumber(),
            validCommand().addressFloor(),
            validCommand().postalCode(),
            validCommand().city(),
            validCommand().province(),
            validCommand().country(),
            validCommand().vatRegime(),
            validCommand().isIntraEu(),
            validCommand().euVatNumber(),
            validCommand().iban(),
            validCommand().paymentMethod(),
            validCommand().paymentDays(),
            validCommand().active()
        );

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));

        assertThatThrownBy(() -> service.create("company-1", command))
            .isInstanceOf(PartnerValidationException.class)
            .hasMessageContaining("dia de pagament");
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

        List<Partner> response = service.list("company-1", "customer");

        assertThat(response).hasSize(1);
        assertThat(response.get(0).isCustomer()).isTrue();
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

    private PartnerCommand validCommand() {
        return new PartnerCommand(
            "Partner",
            "B12345678",
            "mail@test.cat",
            "931000000",
            "",
            "",
            "",
            "",
            "",
            "",
            "ACTIVE",
            null,
            "",
            "",
            BigDecimal.ZERO,
            BigDecimal.ZERO,
            0,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
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

    private PartnerCommand commandWithRoles(boolean isSupplier, boolean isCustomer) {
        return new PartnerCommand(
            "Partner",
            "B12345678",
            "mail@test.cat",
            "931000000",
            "",
            "",
            "",
            "",
            "",
            "",
            "ACTIVE",
            null,
            "",
            "",
            BigDecimal.ZERO,
            BigDecimal.ZERO,
            0,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            isSupplier,
            isCustomer,
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
