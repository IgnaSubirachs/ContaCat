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

Les proves d'integracio de persistencia fan servir Testcontainers amb MySQL real. Si Docker no esta disponible per a la JVM, aquestes proves es marquen com a `skipped` i la resta del suite continua.

Regles d'arquitectura i qualitat:

- Veure `docs/ARCHITECTURE.md`
- Les convencions principals es validen amb tests d'arquitectura (`ArchUnit`) dins de `mvn test`

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

Magatzems:

- `GET /api/core/companies/{companyId}/warehouses`
- `GET /api/core/companies/{companyId}/warehouses/{warehouseId}`
- `POST /api/core/companies/{companyId}/warehouses`
- `PUT /api/core/companies/{companyId}/warehouses/{warehouseId}`
- `DELETE /api/core/companies/{companyId}/warehouses/{warehouseId}` desactiva el magatzem.

Productes:

- `GET /api/core/companies/{companyId}/products`
- `GET /api/core/companies/{companyId}/products/{productId}`
- `POST /api/core/companies/{companyId}/products`
- `PUT /api/core/companies/{companyId}/products/{productId}`
- `DELETE /api/core/companies/{companyId}/products/{productId}` desactiva el producte.

Impostos:

- `GET /api/core/companies/{companyId}/tax-rates`
- `GET /api/core/companies/{companyId}/tax-rates/{taxRateId}`
- `POST /api/core/companies/{companyId}/tax-rates`
- `PUT /api/core/companies/{companyId}/tax-rates/{taxRateId}`
- `DELETE /api/core/companies/{companyId}/tax-rates/{taxRateId}` desactiva l'impost.

Partners:

- `GET /api/core/companies/{companyId}/partners`
- `GET /api/core/companies/{companyId}/partners?role=CUSTOMER`
- `GET /api/core/companies/{companyId}/partners?role=SUPPLIER`
- `GET /api/core/companies/{companyId}/partners/{partnerId}`
- `POST /api/core/companies/{companyId}/partners`
- `PUT /api/core/companies/{companyId}/partners/{partnerId}`
- `DELETE /api/core/companies/{companyId}/partners/{partnerId}` desactiva el partner.

Pla comptable:

- `GET /api/core/companies/{companyId}/accounts`
- `GET /api/core/companies/{companyId}/accounts?group=4`
- `GET /api/core/companies/{companyId}/accounts/{accountId}`
- `POST /api/core/companies/{companyId}/accounts`
- `PUT /api/core/companies/{companyId}/accounts/{accountId}`
- `DELETE /api/core/companies/{companyId}/accounts/{accountId}` desactiva el compte.

Diari comptable:

- `GET /api/core/companies/{companyId}/journal-entries`
- `GET /api/core/companies/{companyId}/journal-entries?startDate=2026-01-01&endDate=2026-12-31`
- `GET /api/core/companies/{companyId}/journal-entries/{entryId}`
- `POST /api/core/companies/{companyId}/journal-entries`
- `POST /api/core/companies/{companyId}/journal-entries/{entryId}/post`

Informes comptables:

- `GET /api/core/companies/{companyId}/accounting/reports/trial-balance`
- `GET /api/core/companies/{companyId}/accounting/reports/ledger/{accountCode}`
- `GET /api/core/companies/{companyId}/accounting/reports/balance-sheet`
- `GET /api/core/companies/{companyId}/accounting/reports/profit-loss`

La migracio `V2__seed_default_company_and_sequences.sql` crea una empresa demo i sequencies inicials per factures de venda, factures de compra i assentaments.

El seguent pas es reforcar aquests informes amb exportacio i continuar la integracio de vendes/compres contra aquest nucli.
