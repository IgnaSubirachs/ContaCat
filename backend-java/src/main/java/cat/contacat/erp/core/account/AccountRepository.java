package cat.contacat.erp.core.account;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AccountRepository extends JpaRepository<Account, String> {

    List<Account> findAllByCompanyIdOrderByCodeAsc(String companyId);

    List<Account> findAllByCompanyIdAndGroupOrderByCodeAsc(String companyId, int group);

    Optional<Account> findByCompanyIdAndCode(String companyId, String code);
}
