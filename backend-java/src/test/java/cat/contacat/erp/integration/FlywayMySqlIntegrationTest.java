package cat.contacat.erp.integration;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.testcontainers.junit.jupiter.Testcontainers;

@SpringBootTest
@Testcontainers(disabledWithoutDocker = true)
class FlywayMySqlIntegrationTest extends AbstractMySqlIntegrationTest {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    void flywayCreatesSchemaAndSeedsCoreData() {
        Integer companies = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM companies", Integer.class);
        Integer sequences = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM document_sequences WHERE document_type = 'JOURNAL_ENTRY'",
            Integer.class
        );
        Integer accounts = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM accounts", Integer.class);

        assertThat(companies).isNotNull().isGreaterThanOrEqualTo(1);
        assertThat(sequences).isNotNull().isGreaterThanOrEqualTo(1);
        assertThat(accounts).isNotNull().isGreaterThanOrEqualTo(5);
    }
}
