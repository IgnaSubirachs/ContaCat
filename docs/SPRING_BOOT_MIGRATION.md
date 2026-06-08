# Pla de Migracio a Spring Boot

## Objectiu

Migrar ContaCat cap a un backend Java/Spring Boot sense perdre el coneixement funcional ja implementat en Python.

## Estrategia

1. Mantenir Python/FastAPI com a referencia funcional temporal.
2. Definir primer el model canonic de dades.
3. Crear el backend Spring Boot en paral.lel.
4. Migrar modul a modul amb tests de paritat.
5. Desactivar endpoints Python quan el modul Java equivalent estigui validat.

## Ordre recomanat

1. Core ERP: empreses, productes, impostos, magatzems, sequencies.
2. Auth i permisos.
3. Partners.
4. Comptabilitat: pla comptable, assentaments, diari, informes.
5. Vendes: pressupostos, comandes, factures.
6. Compres.
7. Inventari.
8. Fiscalitat, banca, tresoreria i RRHH.

## Regles de migracio

- Cap document fiscal pot generar numeracio amb `max(number) + 1`.
- Tota numeracio ha de passar per `document_sequences` amb bloqueig transaccional.
- Cap canvi d'esquema sense migracio Flyway.
- Cap taula nova sense `company_id`, excepte taules estrictament globals.
- Les operacions comptables publicades no s'editen: es reverteixen amb contraassentament.
- Les decisions fiscals han de quedar auditades.

## Estat actual

Creat el modul `backend-java` amb Spring Boot, JPA i Flyway.

Ja hi ha implementat el nucli `core` seguent:

- Empreses
- Sequencies documentals transaccionals
- Magatzems
- Productes
- Impostos
- Partners
- Pla comptable
- Assentaments comptables i llibre diari base

Encara no substitueix cap funcionalitat Python en produccio, pero ja defineix una base consistent per continuar amb informes comptables, vendes i compres.
