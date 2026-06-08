package cat.contacat.erp.core.account.application;

import cat.contacat.erp.core.account.Account;
import cat.contacat.erp.core.account.AccountAlreadyExistsException;
import cat.contacat.erp.core.account.AccountNotFoundException;
import cat.contacat.erp.core.account.AccountRepository;
import cat.contacat.erp.core.account.AccountValidationException;
import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import java.util.List;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AccountApplicationService {

    private final AccountRepository repository;
    private final CompanyRepository companyRepository;

    public AccountApplicationService(AccountRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<Account> list(String companyId, Integer group) {
        ensureCompanyExists(companyId);
        return group == null
            ? repository.findAllByCompanyIdOrderByCodeAsc(companyId)
            : repository.findAllByCompanyIdAndGroupOrderByCodeAsc(companyId, group);
    }

    @Transactional(readOnly = true)
    public Account get(String companyId, String accountId) {
        return findAccountById(companyId, accountId);
    }

    @Transactional
    public Account create(String companyId, AccountCommand command) {
        validateCommand(command);
        Company company = findCompany(companyId);
        String normalizedCode = normalizeCode(command.code());
        ensureCodeAvailable(companyId, normalizedCode, null);

        Account account = new Account();
        account.setCompany(company);
        apply(account, companyId, command, normalizedCode);
        return repository.save(account);
    }

    @Transactional
    public Account update(String companyId, String accountId, AccountCommand command) {
        validateCommand(command);
        Account account = findAccountById(companyId, accountId);
        String normalizedCode = normalizeCode(command.code());
        ensureCodeAvailable(companyId, normalizedCode, accountId);

        apply(account, companyId, command, normalizedCode);
        return repository.save(account);
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

    private void validateCommand(AccountCommand command) {
        String normalizedCode = normalizeCode(command.code());
        if (!normalizedCode.matches("\\d+")) {
            throw new AccountValidationException("El codi del compte ha de ser numeric");
        }
        if (command.group() < 1 || command.group() > 9) {
            throw new AccountValidationException("El grup ha d'estar entre 1 i 9");
        }
        if (Character.getNumericValue(normalizedCode.charAt(0)) != command.group()) {
            throw new AccountValidationException("El primer digit del codi ha de coincidir amb el grup");
        }
    }

    private void apply(Account account, String companyId, AccountCommand command, String normalizedCode) {
        account.setCode(normalizedCode);
        account.setName(command.name().trim());
        account.setAccountType(command.accountType());
        account.setGroup(command.group());
        account.setParentAccount(resolveParent(companyId, command.parentAccountId(), account.getId()));
        account.setActive(command.active() == null || command.active());
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
