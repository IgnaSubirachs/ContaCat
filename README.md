# ![ContaCAT Logo](docs/assets/logo_erp.png) ContaCat v2.0

**El Sistema de Gestió Integral per a la Pime Catalana.**

Desenvolupat amb  **Domain-Driven Design (DDD)**, **FastAPI** i **MySQL**, aquest ERP transformal la gestió empresarial oferint una solució modular, robusta i adaptada a la normativa fiscal espanyola.

---

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

## 🛠️ Stack Tecnològic

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
