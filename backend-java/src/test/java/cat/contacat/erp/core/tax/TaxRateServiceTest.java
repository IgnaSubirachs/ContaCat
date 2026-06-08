package cat.contacat.erp.core.tax;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.tax.api.TaxRateRequest;
import cat.contacat.erp.core.tax.api.TaxRateResponse;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class TaxRateServiceTest {

    @Mock
    private TaxRateRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private TaxRateService service;

    @Test
    void createNormalizesCodeAndPersistsTaxRate() {
        Company company = new Company();
        company.setId("company-1");

        TaxRateRequest request = new TaxRateRequest(
            " iva21 ",
            " IVA general ",
            new BigDecimal("21"),
            " vat ",
            " 472000 ",
            " 477000 ",
            null
        );

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByCompanyIdAndCode("company-1", "IVA21")).thenReturn(Optional.empty());
        when(repository.save(any(TaxRate.class))).thenAnswer(invocation -> {
            TaxRate taxRate = invocation.getArgument(0);
            taxRate.setId("tax-1");
            return taxRate;
        });

        TaxRateResponse response = service.create("company-1", request);

        assertThat(response.id()).isEqualTo("tax-1");
        assertThat(response.companyId()).isEqualTo("company-1");
        assertThat(response.code()).isEqualTo("IVA21");
        assertThat(response.name()).isEqualTo("IVA general");
        assertThat(response.rate()).isEqualByComparingTo(new BigDecimal("21.00"));
        assertThat(response.taxType()).isEqualTo("VAT");
        assertThat(response.inputAccountCode()).isEqualTo("472000");
        assertThat(response.outputAccountCode()).isEqualTo("477000");
        assertThat(response.active()).isTrue();
    }

    @Test
    void createFailsWhenCodeAlreadyExistsInCompany() {
        Company company = new Company();
        company.setId("company-1");

        TaxRate existing = new TaxRate();
        existing.setId("tax-1");
        existing.setCompany(company);
        existing.setCode("IVA21");

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByCompanyIdAndCode("company-1", "IVA21")).thenReturn(Optional.of(existing));

        TaxRateRequest request = new TaxRateRequest(
            "IVA21",
            "IVA general",
            new BigDecimal("21.00"),
            null,
            null,
            null,
            true
        );

        assertThatThrownBy(() -> service.create("company-1", request))
            .isInstanceOf(TaxRateAlreadyExistsException.class);
    }

    @Test
    void deactivateMarksTaxRateAsInactive() {
        Company company = new Company();
        company.setId("company-1");

        TaxRate taxRate = new TaxRate();
        taxRate.setId("tax-1");
        taxRate.setCompany(company);
        taxRate.setRate(new BigDecimal("21.00").setScale(2, RoundingMode.HALF_UP));
        taxRate.setActive(true);

        when(repository.findById("tax-1")).thenReturn(Optional.of(taxRate));

        service.deactivate("company-1", "tax-1");

        assertThat(taxRate.isActive()).isFalse();
        verify(repository).save(taxRate);
    }
}
