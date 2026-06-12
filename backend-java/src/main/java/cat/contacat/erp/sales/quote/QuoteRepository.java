package cat.contacat.erp.sales.quote;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface QuoteRepository extends JpaRepository<Quote, String> {

    List<Quote> findAllByCompanyIdOrderByQuoteDateDescQuoteNumberDesc(String companyId);

    List<Quote> findAllByCompanyIdAndStatusOrderByQuoteDateDescQuoteNumberDesc(String companyId, QuoteStatus status);

    List<Quote> findAllByCompanyIdAndQuoteDateBetweenOrderByQuoteDateDescQuoteNumberDesc(String companyId, LocalDate startDate, LocalDate endDate);

    Optional<Quote> findByCompanyIdAndQuoteNumber(String companyId, String quoteNumber);
}
