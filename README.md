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
- Model core: empreses, magatzems, productes, impostos, partners, comptes i assentaments.
- Informes comptables: balanc de comprovacio, llibre major, balanc de situacio i perdues i guanys.
- Tests unitaris, d'arquitectura i integracio MySQL amb Testcontainers quan Docker es disponible.

Endpoints principals:

- `GET /api/core/companies`
- `GET /api/core/companies/{id}`
- `GET /api/core/companies/{companyId}/accounts`
- `GET /api/core/companies/{companyId}/journal-entries`
- `GET /api/core/companies/{companyId}/accounting/reports/trial-balance`
- `GET /api/core/companies/{companyId}/accounting/reports/balance-sheet`
- `GET /api/core/companies/{companyId}/accounting/reports/profit-loss`

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

## Primera UI visible sobre el backend Java

La capa FastAPI ja pot renderitzar comptabilitat llegint del backend Spring Boot. Configura aquestes variables abans d'arrencar la UI Python:

```powershell
$env:JAVA_ERP_BASE_URL='http://localhost:8080'
# Opcional: fixa una empresa concreta del backend Java
# $env:JAVA_ERP_COMPANY_ID='...'
uvicorn app.interface.api.main:app --reload
```

Amb aquesta configuracio ja es poden veure des de la UI existent:

- `/accounts/`
- `/accounting/`
- `/accounting/journal`
- `/accounting/reports/trial-balance`
- `/accounting/reports/balance-sheet`
- `/accounting/reports/profit-loss`

## Proxims passos

1. Connectar partners, productes i impostos del frontend al backend Java.
2. Connectar vendes i compres contra el nucli comptable Java.
3. Afegir autenticacio i permisos al backend Java.
4. Substituir progressivament els dominis Python antics per adaptadors al backend Spring Boot.

## Notes de migracio

La decisio es mantenir Python com a referencia funcional mentre el nucli Java guanya cobertura. Cada pas hauria de portar migracio Flyway, servei d'aplicacio, endpoint REST i tests.
