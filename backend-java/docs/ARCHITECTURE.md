# Arquitectura i Qualitat

## Objectiu

Fer creixer `backend-java` com un ERP mantenible, testejable i sense codi espagueti.

## Regles obligatories

### TDD

- Cada cas d'us nou ha de comencar per un test que defineixi el comportament.
- Cap bug fix es dona per tancat sense un test que reprodueixi la regressio.
- Els tests unitaris han de provar regles de negoci, no el framework.

### SOLID

- `S`: un controlador no conte logica de negoci.
- `S`: un servei no ha d'acumular responsabilitats de moduls diferents.
- `O`: regles fiscals, comptables i de numeracio s'han de poder ampliar sense reescriure mig modul.
- `L`: substitucions entre implementacions no poden canviar el contracte funcional.
- `I`: no crear interfícies buides o artificials; nomes quan defineixen un contracte amb sentit.
- `D`: el domini no depen de detalls web. Els controladors entren i surten amb DTOs; la logica viu fora.

## Estructura actual admesa

Per cada modul `core/<modul>`:

- `<Modul>.java`: entitats persistents i tipus de domini simples
- `<Modul>Repository.java`: persistencia Spring Data
- `<Modul>Service.java`: casos d'us i regles de negoci
- `api/`: controladors HTTP i DTOs REST

## Regles verificades per tests d'arquitectura

- Els controladors han d'estar a `..api..`.
- Els controladors no poden dependre directament de repositoris.
- Els repositoris han de ser interfícies.
- No s'accepta `field injection`.
- Els moduls de `core` no poden tenir dependencies cyclics.

## Prohibicions

- Cap `max(id)+1` o `max(number)+1` per numeracions funcionals.
- Cap logica fiscal o comptable incrustada a plantilles o controladors.
- Cap classe "helper" o "util" generica per amagar mal disseny.
- Cap entitat publicada modificable si funcionalment ha de ser immutable.

## Seguents passos d'enduriment

- Separar progressivament `application` de `api` per treure DTOs REST dels serveis.
- Introduir proves d'integracio per persistencia i migracions critiques.
- Afegir revisio obligatoria de cicles i dependències abans de cada modul gran.
