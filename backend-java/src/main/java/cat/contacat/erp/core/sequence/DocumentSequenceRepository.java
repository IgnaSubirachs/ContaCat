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
        select sequence
        from DocumentSequence sequence
        where sequence.company.id = :companyId
          and sequence.documentType = :documentType
          and sequence.series = :series
          and sequence.fiscalYear = :fiscalYear
          and sequence.active = true
        """)
    Optional<DocumentSequence> lockActiveSequence(
        @Param("companyId") String companyId,
        @Param("documentType") String documentType,
        @Param("series") String series,
        @Param("fiscalYear") int fiscalYear
    );
}
