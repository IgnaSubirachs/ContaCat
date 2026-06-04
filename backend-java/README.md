# ContaCat ERP - Spring Boot

Aquest directori conte el primer esquelet del futur backend Java/Spring Boot.

## Requisits

- JDK 17 o superior.
- Maven 3.9 o superior.
- MySQL 8.

Validat localment amb JDK 26 i Maven 3.9.12.

Si el terminal encara apunta a Java 8, forca `JAVA_HOME` abans d'executar Maven:

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-26'
$env:PATH="$env:JAVA_HOME\bin;$env:PATH"
```

## Execucio

```bash
mvn spring-boot:run
```

Validacio rapida:

```bash
mvn validate -DskipTests
mvn test
```

Variables principals:

- `DATABASE_URL`: JDBC URL, per exemple `jdbc:mysql://localhost:3306/erpdb?useUnicode=true&characterEncoding=utf8&serverTimezone=Europe/Madrid`
- `DB_USER`
- `DB_PASSWORD`

## Decisions inicials

- Spring Boot 3.5.x amb Java 17 per mantenir una base empresarial estable.
- JPA/Hibernate per al model de domini persistent.
- Flyway per migracions SQL versionades.
- `ddl-auto: validate` per evitar que Hibernate canviï l'esquema sense migracio explicita.

## Nucli migrat

El primer paquet `core` replica el model ERP canonic definit tambe a Alembic:

- `Company`
- `Warehouse`
- `Product`
- `TaxRate`
- `DocumentSequence`

## API core disponible

Empreses:

- `GET /api/core/companies`
- `GET /api/core/companies/{id}`
- `POST /api/core/companies`
- `PUT /api/core/companies/{id}`
- `DELETE /api/core/companies/{id}` desactiva l'empresa.

Sequencies documentals:

- `POST /api/core/sequences/next`

La migracio `V2__seed_default_company_and_sequences.sql` crea una empresa demo i sequencies inicials per factures de venda, factures de compra i assentaments.

El seguent pas es implementar serveis d'aplicacio i endpoints REST per productes, magatzems i impostos abans de migrar comptabilitat, vendes i compres.
