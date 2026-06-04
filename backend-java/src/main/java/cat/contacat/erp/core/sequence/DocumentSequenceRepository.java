package cat.contacat.erp.core.sequence;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import jakarta.persistence.LockModeType;

public interface DocumentSequenceRepository extends JpaRepository<DocumentSequence, String> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("""
        select seq
        from DocumentSequence seq
        where seq.company.id = :companyId
          and seq.documentType = :documentType
          and seq.series = :series
          and seq.fiscalYear = :fiscalYear
          and seq.active = true
        """)
    Optional<DocumentSequence> lockActiveSequence(
        @Param("companyId") String companyId,
        @Param("documentType") String documentType,
        @Param("series") String series,
        @Param("fiscalYear") int fiscalYear
    );
}
