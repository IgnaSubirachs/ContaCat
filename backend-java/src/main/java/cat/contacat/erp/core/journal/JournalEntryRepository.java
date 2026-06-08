package cat.contacat.erp.core.journal;

import java.time.LocalDate;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface JournalEntryRepository extends JpaRepository<JournalEntry, String> {

    List<JournalEntry> findAllByCompanyIdOrderByEntryDateDescEntryNumberDesc(String companyId);

    List<JournalEntry> findAllByCompanyIdAndEntryDateBetweenOrderByEntryDateDescEntryNumberDesc(
        String companyId,
        LocalDate startDate,
        LocalDate endDate
    );

    List<JournalEntry> findAllByCompanyIdOrderByEntryDateAscEntryNumberAsc(String companyId);

    List<JournalEntry> findAllByCompanyIdAndEntryDateBetweenOrderByEntryDateAscEntryNumberAsc(
        String companyId,
        LocalDate startDate,
        LocalDate endDate
    );
}
