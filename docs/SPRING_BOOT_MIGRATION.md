# Pla de Migracio a Spring Boot

## Objectiu

Migrar ContaCat cap a un backend Java/Spring Boot sense perdre el coneixement funcional ja implementat en Python.

## Estrategia

1. Mantenir Python/FastAPI com a referencia funcional temporal.
2. Definir primer el model canonic de dades.
3. Crear el backend Spring Boot en paral.lel.
4. Migrar modul a modul amb tests de paritat.
5. Desactivar endpoints Python quan el modul Java equivalent estigui validat.

## Regla de desenvolupament a partir d'ara

No s'afegeix nova logica de negoci nomes a Python.

Cada millora funcional s'implementa com un tall vertical:

1. Definir el comportament professional, les regles de negoci i el contracte REST.
2. Implementar domini, servei d'aplicacio, migracio Flyway i API a Java.
3. Cobrir regles i regressions amb tests Java.
4. Connectar la UI FastAPI a l'API Java mitjancant un adaptador.
5. Fer proves de paritat i del flux complet.
6. Retirar la persistencia i logica Python substituides.

Python pot continuar rebent millores transversals de presentacio, navegacio,
seguretat de la UI i adaptadors, pero no ha de convertir-se en el nou sistema
de registre dels moduls que s'estan migrant.

## Migracio del frontend

El nou frontend viu a `frontend-angular/` i es connecta directament als
contractes REST de Spring Boot. La UI FastAPI es mantindra nomes com a pont
temporal fins que cada pantalla Angular tingui paritat funcional i proves.

Regles:

- Cap logica de negoci dins components Angular.
- Models, context d'empresa i clients HTTP viuen a `src/app/core`.
- Les pantalles s'organitzen per domini funcional a `src/app/features`.
- Cada pantalla Angular nova ha de consumir exclusivament endpoints Java.
- Una ruta FastAPI nomes es retira quan el flux Angular equivalent esta validat.

## Criteri de finalitzacio d'un modul

Un modul no es considera migrat nomes per tenir endpoints Java. Ha de complir:

- Esquema gestionat exclusivament amb Flyway.
- Totes les dades segregades per `company_id`.
- Regles de negoci cobertes per tests unitaris.
- Persistencia i migracions critiques cobertes per tests d'integracio.
- UI llegint i escrivint exclusivament contra l'API Java.
- Errors funcionals traduïts a respostes REST estables.
- Endpoint Python antic desactivat o reduit a adaptador sense logica.
- Documentacio del contracte i proves de paritat completades.

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

## Proper tall vertical: Partners

Partners sera el patro de migracio completa abans d'obrir mes moduls.

Treball pendent:

1. Ampliar el model Java amb dades comercials, bancaries i comptables.
2. Modelar contactes, contractes i periodificacions com a registres relacionats,
   no com a text lliure permanent.
3. Afegir migracio Flyway i tests de regles de negoci.
4. Ampliar `JavaErpClient` amb CRUD de partners.
5. Connectar les pantalles `/partners/` exclusivament al backend Java.
6. Fer proves de paritat i retirar la persistencia Python de partners.

### Regla especifica mentre partners no estigui migrat a Java

- No s'afegeixen nous camps funcionals de partners nomes al model Python.
- Si cal una millora urgent de UI, es permet nomes a nivell de presentacio.
- Qualsevol ampliacio de dades de partners ha de neixer a `backend-java` i
  arribar a FastAPI a traves de l'adaptador.

Despres de partners, l'ordre recomanat es:

1. Comptabilitat i pla comptable, completant la integracio ja iniciada.
2. Vendes, de pressupost a factura publicada.
3. Compres, de comanda a factura i assentament.
4. Inventari.
5. Banca i tresoreria.
6. Fiscalitat i recursos humans.
