package cat.contacat.erp.core.account.api;

import cat.contacat.erp.core.account.application.AccountApplicationService;
import cat.contacat.erp.core.account.application.AccountCommand;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/core/companies/{companyId}/accounts")
public class AccountController {

    private final AccountApplicationService service;

    public AccountController(AccountApplicationService service) {
        this.service = service;
    }

    @GetMapping
    public List<AccountResponse> list(@PathVariable String companyId, @RequestParam(required = false) Integer group) {
        return service.list(companyId, group).stream().map(AccountResponse::from).toList();
    }

    @GetMapping("/{accountId}")
    public AccountResponse get(@PathVariable String companyId, @PathVariable String accountId) {
        return AccountResponse.from(service.get(companyId, accountId));
    }

    @PostMapping
    public ResponseEntity<AccountResponse> create(@PathVariable String companyId, @Valid @RequestBody AccountRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(AccountResponse.from(service.create(companyId, toCommand(request))));
    }

    @PutMapping("/{accountId}")
    public AccountResponse update(
        @PathVariable String companyId,
        @PathVariable String accountId,
        @Valid @RequestBody AccountRequest request
    ) {
        return AccountResponse.from(service.update(companyId, accountId, toCommand(request)));
    }

    @DeleteMapping("/{accountId}")
    public ResponseEntity<Void> deactivate(@PathVariable String companyId, @PathVariable String accountId) {
        service.deactivate(companyId, accountId);
        return ResponseEntity.noContent().build();
    }

    private AccountCommand toCommand(AccountRequest request) {
        return new AccountCommand(
            request.code(),
            request.name(),
            request.accountType(),
            request.group(),
            request.parentAccountId(),
            request.active()
        );
    }
}
