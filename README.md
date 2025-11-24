# ERP Català

Sistema ERP modular desenvolupat amb Domain-Driven Design (DDD), FastAPI i MySQL.

## Característiques

- **Arquitectura DDD**: Separació clara entre Domini, Infraestructura i Interfície
- **Modular**: Mòduls independents per RRHH, Comptabilitat, Pressupostos, Finances, Conciliació Bancària i Partners
- **Interfície Web**: Interfície web moderna amb FastAPI
- **Docker**: Desplegament fàcil amb Docker Compose

## Mòduls Implementats

- ✅ **Partners (Clients i Proveïdors)**: Gestió completa de clients i proveïdors
- ✅ **HR (RRHH)**: Gestió d'empleats, càrrecs, departaments i salaris
- 🚧 **Accounts (Comptes)**: Pla comptable
- 📋 **Accounting (Comptabilitat)**: Gestió comptable (en desenvolupament)
- 📋 **Budgets (Pressupostos)**: Gestió de pressupostos (en desenvolupament)
- 📋 **Finance (Finances)**: Gestió financera (en desenvolupament)
- 📋 **Banking (Conciliació)**: Conciliació bancària (en desenvolupament)

## Requisits

- Docker
- Docker Compose

## Instal·lació i Execució

1. Clona el repositori
2. Executa amb Docker Compose:

```bash
docker-compose up --build
```

3. Accedeix a l'aplicació:
   - Interfície Web: http://localhost:8000
   - Partners: http://localhost:8000/partners/
   - Documentació API: http://localhost:8000/docs

## Estructura del Projecte

```
app/
├── domain/              # Capa de Domini (entitats, repositoris, serveis)
│   ├── accounts/
│   ├── partners/
│   ├── hr/
│   └── ...
├── infrastructure/      # Capa d'Infraestructura (persistència)
│   ├── db/
│   └── persistence/
│       ├── accounts/
│       ├── partners/
│       └── ...
└── interface/          # Capa d'Interfície (API, Web)
    ├── api/
    │   ├── routers/
    │   └── main.py
    └── web/
        ├── templates/
        └── static/
```

## Tecnologies

- **Backend**: Python 3.12, FastAPI
- **Base de Dades**: MySQL 8
- **ORM**: SQLAlchemy 2.0
- **Contenidors**: Docker, Docker Compose
- **Frontend**: HTML, CSS (plantilles Jinja2)
