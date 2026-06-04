# ContaCat ERP

ContaCat es un ERP pensat per a pimes catalanes. L'objectiu es construir una alternativa moderna a eines com SAP Business One o A3, amb comptabilitat, facturacio, fiscalitat, inventari i processos d'empresa adaptats al context catala i espanyol.

El projecte conserva una base Python/FastAPI existent, pero la direccio tecnica actual es migrar el nucli empresarial cap a Java amb Spring Boot.

## Estat actual

- `app/`: aplicacio Python/FastAPI existent.
- `migrations/`: migracions SQL de la base Python.
- `backend-java/`: nou backend Spring Boot.
- `docs/SPRING_BOOT_MIGRATION.md`: pla de migracio cap a Java.

## Backend Java

El modul `backend-java` ja incorpora:

- Spring Boot 3.5.x.
- JPA/Hibernate amb Flyway.
- Model core: empreses, magatzems, productes, impostos i sequencies documentals.
- CRUD inicial d'empreses.
- Servei transaccional per reservar numeros documentals.
- Seed inicial d'una empresa demo i sequencies per a factures de venda, factures de compra i assentaments.

Endpoints principals:

- `GET /api/core/companies`
- `GET /api/core/companies/{id}`
- `POST /api/core/companies`
- `PUT /api/core/companies/{id}`
- `DELETE /api/core/companies/{id}`
- `POST /api/core/sequences/next`

## Requisits

- JDK 17 o superior. Validat localment amb JDK 26.
- Maven 3.9 o superior.
- MySQL 8 per executar l'aplicacio completa.
- Python 3 per validar la base existent.

Si el terminal apunta a una versio antiga de Java:

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-26'
$env:PATH="$env:JAVA_HOME\bin;$env:PATH"
```

## Validacio rapida

```powershell
mvn -f backend-java\pom.xml test
python -m compileall -q app migrations
```

## Execucio del backend Java

Configura la connexio a MySQL amb variables d'entorn:

```powershell
$env:DATABASE_URL='jdbc:mysql://localhost:3306/erpdb?useUnicode=true&characterEncoding=utf8&serverTimezone=Europe/Madrid'
$env:DB_USER='root'
$env:DB_PASSWORD='password'
mvn -f backend-java\pom.xml spring-boot:run
```

## Proxims passos

1. Crear endpoints core per productes, magatzems i impostos.
2. Migrar clients/proveidors i documents comercials.
3. Migrar comptabilitat: pla comptable, assentaments, diari i balanços.
4. Afegir autenticacio i permisos al backend Java.
5. Fer que el frontend consumeixi progressivament l'API Spring Boot.

## Notes de migracio

La decisio es mantenir Python com a referencia funcional mentre el nucli Java guanya cobertura. Cada pas hauria de portar migracio Flyway, servei d'aplicacio, endpoint REST i tests.
