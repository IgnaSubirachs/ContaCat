package cat.contacat.erp.core.account;

import cat.contacat.erp.core.account.api.AccountRequest;
import cat.contacat.erp.core.account.api.AccountResponse;
import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import java.util.List;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AccountService {

    private final AccountRepository repository;
    private final CompanyRepository companyRepository;

    public AccountService(AccountRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<AccountResponse> list(String companyId, Integer group) {
        ensureCompanyExists(companyId);
        List<Account> accounts = group == null
            ? repository.findAllByCompanyIdOrderByCodeAsc(companyId)
            : repository.findAllByCompanyIdAndGroupOrderByCodeAsc(companyId, group);
        return accounts.stream().map(AccountResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public AccountResponse get(String companyId, String accountId) {
        return AccountResponse.from(findAccountById(companyId, accountId));
    }

    @Transactional
    public AccountResponse create(String companyId, AccountRequest request) {
        validateRequest(request);
        Company company = findCompany(companyId);
        String normalizedCode = normalizeCode(request.code());
        ensureCodeAvailable(companyId, normalizedCode, null);

        Account account = new Account();
        account.setCompany(company);
        apply(account, companyId, request, normalizedCode);
        return AccountResponse.from(repository.save(account));
    }

    @Transactional
    public AccountResponse update(String companyId, String accountId, AccountRequest request) {
        validateRequest(request);
        Account account = findAccountById(companyId, accountId);
        String normalizedCode = normalizeCode(request.code());
        ensureCodeAvailable(companyId, normalizedCode, accountId);

        apply(account, companyId, request, normalizedCode);
        return AccountResponse.from(repository.save(account));
    }

    @Transactional
    public void deactivate(String companyId, String accountId) {
        Account account = findAccountById(companyId, accountId);
        account.setActive(false);
        repository.save(account);
    }

    public Account findAccountByCode(String companyId, String code) {
        return repository.findByCompanyIdAndCode(companyId, normalizeCode(code))
            .orElseThrow(() -> new AccountNotFoundException(companyId, code));
    }

    private Account findAccountById(String companyId, String accountId) {
        Account account = repository.findById(accountId)
            .orElseThrow(() -> new AccountNotFoundException(companyId, accountId));
        if (!Objects.equals(account.getCompany().getId(), companyId)) {
            throw new AccountNotFoundException(companyId, accountId);
        }
        return account;
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

    private void ensureCodeAvailable(String companyId, String code, String currentAccountId) {
        repository.findByCompanyIdAndCode(companyId, code)
            .filter(existing -> !Objects.equals(existing.getId(), currentAccountId))
            .ifPresent(existing -> { throw new AccountAlreadyExistsException(companyId, code); });
    }

    private void validateRequest(AccountRequest request) {
        String normalizedCode = normalizeCode(request.code());
        if (!normalizedCode.matches("\\d+")) {
            throw new AccountValidationException("El codi del compte ha de ser numeric");
        }
        if (request.group() < 1 || request.group() > 9) {
            throw new AccountValidationException("El grup ha d'estar entre 1 i 9");
        }
        if (Character.getNumericValue(normalizedCode.charAt(0)) != request.group()) {
            throw new AccountValidationException("El primer digit del codi ha de coincidir amb el grup");
        }
    }

    private void apply(Account account, String companyId, AccountRequest request, String normalizedCode) {
        account.setCode(normalizedCode);
        account.setName(request.name().trim());
        account.setAccountType(request.accountType());
        account.setGroup(request.group());
        account.setParentAccount(resolveParent(companyId, request.parentAccountId(), account.getId()));
        account.setActive(request.active() == null || request.active());
    }

    private Account resolveParent(String companyId, String parentAccountId, String currentAccountId) {
        if (parentAccountId == null || parentAccountId.isBlank()) {
            return null;
        }
        Account parent = findAccountById(companyId, parentAccountId);
        if (Objects.equals(parent.getId(), currentAccountId)) {
            throw new AccountValidationException("Un compte no pot ser pare de si mateix");
        }
        return parent;
    }

    private String normalizeCode(String code) {
        return code.trim();
    }
}
