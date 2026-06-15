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
- Els assentaments en esborrany es poden editar abans de publicar-los.
- Les operacions comptables publicades no s'editen: es reverteixen amb contraassentament.
- Les decisions fiscals han de quedar auditades.

## Importacio de factures PDF

Spring Boot exposa `POST /api/core/companies/{companyId}/journal-entry-imports/supplier-invoice-pdf`.
El document PDF es llegeix mitjancant l'adaptador `InvoiceDocumentReader` i genera
un assentament en estat `DRAFT` amb una proposta de compra, IVA suportat i
proveidor. La resposta inclou confiança i avisos perquè l'usuari revisi i editi
la proposta abans de publicar-la.

L'adaptador actual utilitza Apache PDFBox per a PDFs amb text. Un lector OCR o
un lector extern existent es pot incorporar implementant `InvoiceDocumentReader`
sense modificar el servei comptable ni els endpoints.

## Estat actual

Spring Boot ja gestiona el nucli ERP, partners, comptabilitat base, informes,
llicencies i el flux comercial de pressupost, comanda i factura de venda.
Angular ja disposa del shell ERP i de les primeres pantalles comercials.

## Mapa complet de moduls

Tots els moduls funcionals existents a Python s'han de portar progressivament a
Spring Boot i Angular. Python es retirara quan ja no quedi cap flux de negoci
que en depengui.

| Area | Moduls | Estat |
| --- | --- | --- |
| Core ERP | Empreses, sequencies, productes, impostos, magatzems | Backend Java implementat |
| Administracio | Usuaris, rols, permisos, configuracio, llicencies | Llicencies implementades; auth i configuracio pendents |
| Tercers | Clients, proveidors i dades comercials | Backend Java implementat; llistat Angular implementat |
| Comptabilitat | Pla comptable, assentaments, diari i informes | Backend Java implementat; Angular pendent |
| Vendes | Pressupostos, comandes i factures | Backend Java implementat; Angular parcial |
| Compres | Comandes, recepcions i factures de proveidor | Pendent |
| Inventari | Stock, moviments, lots, series i valoracio | Pendent |
| Tresoreria | Cobraments, pagaments, previsions i caixa | Pendent |
| Banca | Comptes, extractes i conciliacio bancaria | Pendent |
| Fiscalitat | IVA, IRPF, models, SII i auditories fiscals | Pendent |
| Actius | Actius fixos i amortitzacions | Pendent |
| Pressupostos | Pressupostos financers i control de desviacions | Pendent |
| Recursos humans | Empleats, nomines i obligacions laborals | Pendent |
| Analitica | KPIs, informes executius i exportacions | Pendent |
| Serveis transversals | Auditoria, documents, email, IA i internacionalitzacio | Pendent |

## Ordre d'implementacio vigent

1. Tancar vendes: detall, emissio, cobrament, rectificatives i assentament automatic.
2. Completar Angular per partners, productes i comptabilitat.
3. Migrar compres de comanda a factura i assentament.
4. Migrar inventari i integrar-lo amb vendes i compres.
5. Migrar tresoreria, banca i conciliacio.
6. Migrar fiscalitat, SII i models oficials.
7. Migrar actius, pressupostos financers i recursos humans.
8. Completar analitica, auditoria, documents, email, IA i multidioma.
