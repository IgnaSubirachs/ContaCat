package cat.contacat.erp.core.account;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.account.api.AccountRequest;
import cat.contacat.erp.core.account.api.AccountResponse;
import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class AccountServiceTest {

    @Mock
    private AccountRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @InjectMocks
    private AccountService service;

    @Test
    void createPersistsNormalizedAccount() {
        Company company = new Company();
        company.setId("company-1");
        AccountRequest request = new AccountRequest("430000", " Clients ", AccountType.ASSET, 4, null, null);

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByCompanyIdAndCode("company-1", "430000")).thenReturn(Optional.empty());
        when(repository.save(any(Account.class))).thenAnswer(invocation -> {
            Account account = invocation.getArgument(0);
            account.setId("account-1");
            return account;
        });

        AccountResponse response = service.create("company-1", request);

        assertThat(response.id()).isEqualTo("account-1");
        assertThat(response.code()).isEqualTo("430000");
        assertThat(response.name()).isEqualTo("Clients");
        assertThat(response.accountType()).isEqualTo(AccountType.ASSET);
    }

    @Test
    void createFailsWhenCodeAlreadyExists() {
        Company company = new Company();
        company.setId("company-1");
        Account existing = new Account();
        existing.setId("account-1");
        existing.setCompany(company);
        existing.setCode("430000");

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(repository.findByCompanyIdAndCode("company-1", "430000")).thenReturn(Optional.of(existing));

        assertThatThrownBy(() -> service.create("company-1", new AccountRequest("430000", "Clients", AccountType.ASSET, 4, null, true)))
            .isInstanceOf(AccountAlreadyExistsException.class);
    }

    @Test
    void createFailsWhenGroupDoesNotMatchCode() {
        assertThatThrownBy(() -> service.create("company-1", new AccountRequest("430000", "Clients", AccountType.ASSET, 5, null, true)))
            .isInstanceOf(AccountValidationException.class);
    }

    @Test
    void deactivateMarksAccountInactive() {
        Company company = new Company();
        company.setId("company-1");
        Account account = new Account();
        account.setId("account-1");
        account.setCompany(company);
        account.setActive(true);

        when(repository.findById("account-1")).thenReturn(Optional.of(account));

        service.deactivate("company-1", "account-1");

        assertThat(account.isActive()).isFalse();
        verify(repository).save(account);
    }
}
