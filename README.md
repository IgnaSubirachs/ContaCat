# ERP Català

Sistema ERP modular desenvolupat amb Domain-Driven Design (DDD), FastAPI i MySQL.

## Característiques

- **Arquitectura DDD**: Separació clara entre Domini, Infraestructura i Interfície
- **Modular**: Mòduls independents per RRHH, Comptabilitat, Pressupostos, Finances, Conciliació Bancària i Partners
- **Interfície Web**: Interfície web moderna amb FastAPI
- **Docker**: Desplegament fàcil amb Docker Compose

## Mòduls Implementats

- ✅ **Partners (Clients i Proveïdors)**: Gestió completa de clients i proveïdors. Funcionalitats: llistat, creació, edició, supressió, gestió de documents adjunts i validació de NIF/CIF.
  - **API REST**:
    - `GET /partners/` – llista de partners
    - `POST /partners/create` – crear nou partner
    - `GET /partners/edit/{id}` – formulari d'edició
    - `POST /partners/edit/{id}` – actualitzar partner
    - `POST /partners/delete/{id}` – eliminar partner
    - `GET /partners/api/list` – llista en JSON
- ✅ **HR (RRHH)**: Gestió d'empleats, càrrecs, departaments i salaris
- ✅ **Accounts (Comptes)**: Pla comptable amb grups i tipus de comptes
- ✅ **Accounting (Comptabilitat)**: Gestió comptable completa amb Pla General Comptable, Assentaments, Llibres i Informes Financers (Balanç i PyG).
- ✅ **Assets (Actius Fixes)**: Gestió d'actius fixes amb amortització automàtica i integració amb Comptabilitat (assentaments automàtics).
- ✅ **Inventory (Inventari)**: Gestió d'stock amb articles, moviments d'entrada/sortida i control de nivells.
- ✅ **User Management (Gestió d'Usuaris)**: Sistema d'autenticació i autorització amb JWT. Rols: ADMIN, MANAGER, USER, READ_ONLY. Panell d'administració per a gestió d'usuaris.
- 📋 **Budgets (Pressupostos)**: Gestió de pressupostos (en desenvolupament)
- 📋 **Finance (Finances)**: Gestió financera (en desenvolupament)
- 📋 **Banking (Conciliació)**: Conciliació bancària (en desenvolupament)



## Versió Escriptori (Nou!)

L'ERP ara disposa d'una versió d'escriptori nativa per a Windows.

### Construcció i Execució

1.  **Construir l'executable**:
    ```bash
    c:\ERP\build_exe.bat
    ```
    Això generarà l'arxiu `dist\ERP_Catala\ERP_Catala.exe`.

2.  **Executar**:
    - Assegura't que el servidor MySQL està en marxa.
    - Executa `ERP_Catala.exe`.
    - S'obrirà una finestra amb l'aplicació (sense navegador).

## Requisits

- Docker (per a la versió contenidoritzada)
- Python 3.12+ (per a execució local/escriptori)
- MySQL 8

## Instal·lació i Execució (Web / Docker)

1. Clona el repositori
2. Executa amb Docker Compose:

```bash
docker-compose up --build
```

3. Accedeix a l'aplicació:
   - Interfície Web: http://localhost:8000
   - Partners: http://localhost:8000/partners/
   - Documentació API: http://localhost:8000/docs

4. Inicialitza l'usuari administrador (només la primera vegada):
```bash
python create_admin_user.py
```
Credencials per defecte: `admin` / `admin123` (canvia-les després del primer login!)

## Interfície d'Usuari

L'aplicació disposa d'una **interfície fosca professional** amb icones realistes 3D generades per IA. Tots els mòduls principals (Comptabilitat, RRHH, Partners, Vendes) tenen un disseny consistent i modern.

## Gestió d'Usuaris i Seguretat

- **Autenticació JWT**: Sistema d'autenticació segur amb tokens JWT
- **Control d'Accés Basat en Rols (RBAC)**:
  - **ADMIN**: Accés total, gestió d'usuaris
  - **MANAGER**: Accés complet a mòduls de negoci
  - **USER**: Accés estàndard
  - **READ_ONLY**: Només lectura
- **Panell d'Administració**: Gestió completa d'usuaris (només per a ADMIN)
- **Login**: http://localhost:8000/auth/login-page
- **Gestió d'Usuaris**: http://localhost:8000/auth/users-page

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
- **Escriptori**: pywebview, PyInstaller
- **Contenidors**: Docker, Docker Compose
- **Frontend**: HTML, CSS (plantilles Jinja2)

## Llicència

Aquest projecte està publicat sota la **PolyForm Noncommercial License 1.0.0**.

Pots utilitzar, modificar i distribuir aquest programari lliurement per a **usos no comercials**.
Per a qualsevol ús comercial, si us plau contacta amb l'autor per obtenir una llicència comercial.

Consulta el fitxer [LICENSE](LICENSE) per a més detalls.
