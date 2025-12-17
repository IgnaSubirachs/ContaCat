# ![ContaCAT Logo](docs/assets/logo_erp.png) ContaCat v2.0

**El Sistema de Gestió Integral per a la Pime Catalana.**

Desenvolupat amb  **Domain-Driven Design (DDD)**, **FastAPI** i **MySQL**, aquest ERP transformal la gestió empresarial oferint una solució modular, robusta i adaptada a la normativa fiscal espanyola.

---

## 🚀 Novetats# ContaCAT ERP - Sistema ERP en Català

Sistema ERP complet desenvolupat en Python amb FastAPI, dissenyat específicament per empreses catalanes.

## ✨ Actualitzacions Recents (Desembre 2024)

### Millores Crítiques Implementades

**Interfície d'Usuari:**
- ✅ **Sidebar Scrollable**: Solució CSS per scroll vertical al menú lateral
- ✅ **Navegació Comptabilitat**: Nova secció "Comptabilitat" al sidebar amb Diari, Pla Comptable i Balanç de Comprovació
- ✅ **URLs Consistents**: Corregides totes les rutes del sidebar per ser coherents
- ✅ **AI Chat Interface**: Nova interfície web completa per prediccions de comptes comptables amb IA
- ✅ **Cat Assistant**: Navegació millorada amb enllaços correctes a la pàgina d'IA
- ✅ **Topbar Navigation**: Corregits enllaços de configuració i perfil
- ✅ **Dashboard**: Gràfics Chart.js funcionant correctament, símbol € arreglat

**Mòdul de Comptabilitat:**
- ✅ **Llibre Diari**: Ruta GET `/accounting/journal` per llistar assentaments
- ✅ **Creació d'Assentaments**: Ruta GET `/accounting/journal/create` amb formulari complet
- ✅ **Template Dinàmic**: Formulari interactiu amb validació Deure=Haver en temps real
- ✅ **Gestió d'Errors**: Error handling millorat amb missatges descriptius
- ✅ **Selector de Comptes**: Autocomplete amb tots els comptes del pla comptable

**Backend i Base de Dades:**
- ✅ **PDF Generation Fix**: Import DocumentService corregit a `pdf_service.py`
- ✅ **Settings Module**: Migració MySQL completada amb camps SMTP i SII
- ✅ **Authentication**: Sistema d'autenticació opcional per routers `/ai/` i `/settings/`
- ✅ **Templates**: Auto-reload activat per desenvolupament més àgil
- ✅ **Docker**: Deployment completament funcional amb MySQL

**Fitxers Principals Actualitzats:**
- `frontend/templates/accounting/journal/create.html` (NOU - 254 línies)
- `frontend/templates/components/sidebar.html` (reorganitzat i estès)
- `frontend/static/css/styles.css` (fixes de scroll i flexbox)
- `app/interface/api/routers/accounting.py` (noves rutes i error handling)
- `app/domain/sales/pdf_service.py` (import fix)
- `frontend/templates/ai/chat.html` (NOU - 239 línies)
- `frontend/templates/components/topbar.html`
- `frontend/templates/components/cat_assistant.html`
- `app/interface/api/routers/ai.py`
- `app/interface/api/routers/settings.py`
- `migrations/add_smtp_sii_to_company_settings.sql` (NOU)

## 🚀 Novetats "CEO Plan" (Desembre 2025)

Hem completat un sprint intensiu per dotar l'ERP de capacitats executives reals:

1.  **Panell de Control Executiu (Dashboard v2)**:
    -   KPIs en Temps Real: Vendes, Tresoreria, Pendents de Conciliació.
    -   Gràfics interactius (Chart.js) d'evolució de vendes.
2.  **Conciliació Bancària Automàtica**:
    -   Suport per a **Norma 43** (format bancari espanyol).
    -   Motor de suggeriments amb IA/Regles per casar moviments amb factures.
3.  **Fiscalitat i Models**:
    -   **Model 303 (IVA)**: Autoliquidació automàtica llegint del Diari Comptable.
    -   Generació de PDFs professionals (Factures i Nòmines) amb imatge corporativa.
4.  **Configuració Centralitzada**:
    -   Gestió de dades d'empresa (NIF, Logo, Adreça) que s'injecten a tots els documents.

---

## 🧩 Mòduls Principals

### 1. Finances i Comptabilitat
-   **Comptabilitat General**: Assentaments, Llibre Major i Diari.
-   **Pla General Comptable (PGC)**: Gestió de comptes i subcomptes.
-   **Tresoreria**: Control de Caixa i Bancs. Importació de Norma 43.
-   **Fiscalitat**: Càlcul de models oficials (AEAT).

### 2. Vendes i Relacions
-   **Cicle de Venda**: Pressupostos -> Comandes -> Factures.
-   **Partners**: CRM bàsic per a Clients i Proveïdors.
-   **Facturació**: Generació de PDFs automàtiga.

### 3. Recursos Humans
-   **Gestió d'Empleats**: Fitxa completa.
-   **Nòmines**: Generació de rebuts de salari (PDF).

### 4. Operacions
-   **Inventari**: Control d'estoc en temps real.
-   **Analítica**: Ràtios financeres i informes de rendiment.

---

## � Estructura del Projecte

```
app/
├── domain/              # Capa de Domini (entitats, repositoris, serveis)
├── infrastructure/      # Capa d'Infraestructura (persistència)
└── interface/           # Capa d'Interfície (API, Web)

scripts/                 # Scripts d'utilitat
├── setup/               # Inicialització i migracions
├── maintenance/         # Eines de manteniment (reset pwd)
└── data/                # Generació de dades de prova

docs/                    # Documentació addicional
```

## �🛠️ Stack Tecnològic

-   **Backend**: Python 3.12, FastAPI (Async).
-   **Arquitectura**: DDD (Domain, Infrastructure, Interface).
-   **Base de Dades**: MySQL 8 (SQLAlchemy ORM).
-   **Frontend**: Jinja2 Templates, Bootstrap 5, Chart.js.
-   **Infrastructure**: Docker & Docker Compose.

---

## ⚡ Instal·lació Ràpida

### Amb Docker (Recomanat)

1.  **Clonar i Arrencar**:
    ```bash
    git clone https://github.com/IgnaSubirachs/ContaCat-DEMO.git
    cd ContaCat-DEMO
    docker-compose up --build
    ```

2.  **Accedir**:
    -   Web: http://localhost:8000
    -   Login: `admin` / `admin123`

### Execució Local (Desenvolupament)

Requeriments: Python 3.12+, MySQL local.

1.  Crear entorn virtual: `python -m venv venv`
2.  Instal·lar dependències: `pip install -r requirements.txt`
3.  Executar servidor: `python check_production_ready.py` (Script d'arrencada).

---

## 📄 Llicència

Aquest projecte es distribueix sota la **PolyForm Noncommercial License 1.0.0**.
Pots utilitzar-lo lliurement per a fins no comercials o educatius. Per a ús comercial, contacta amb l'autor.

---
*Desenvolupat amb ❤️ i IA per Ignasi Subirachs | Barcelona, 2025*
