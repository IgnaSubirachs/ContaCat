# Guia Ràpida: Com Provar els Informes Financers

## Pas 1: Iniciar el Servidor

Obre una terminal i executa:

```bash
cd c:\ERP
python -m uvicorn app.interface.api.main:app --reload
```

Hauries de veure alguna cosa com:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Pas 2: Accedir als Informes

Obre el navegador i visita:

### Pàgina Principal de Comptabilitat
http://localhost:8000/accounting

### Balanç de Situació
http://localhost:8000/accounting/reports/balance-sheet

### Compte de Pèrdues i Guanys
http://localhost:8000/accounting/reports/profit-loss

## Pas 3: Provar Exportació

Des de qualsevol informe, clica els botons:
- **Exportar PDF**: Descarregarà un fitxer PDF
- **Exportar Excel**: Descarregarà un fitxer Excel

## Errors Comuns

### Error: "Internal Server Error"

**Causa possible 1**: La base de dades no està en marxa

**Solució**: Assegura't que MySQL/MariaDB està executant-se i que pots connectar-te

**Causa possible 2**: No hi ha dades a la base de dades

**Solució**: Els informes funcionaran encara que no hi hagi dades, però mostraran taules buides

**Causa possible 3**: Error d'importació de mòduls

**Solució**: Verifica que has instal·lat totes les dependències:
```bash
pip install reportlab openpyxl pandas
```

### Error: "404 Not Found"

**Causa**: URL incorrecta

**Solució**: Verifica que l'URL comença amb `http://localhost:8000/accounting/`

### Error: "Connection Refused"

**Causa**: El servidor no està en marxa

**Solució**: Executa `python -m uvicorn app.interface.api.main:app --reload`

## Verificar que Tot Funciona

Executa aquest script per verificar que tot està correcte:

```bash
python -c "import sys; sys.path.insert(0, 'c:\\ERP'); from app.interface.api.routers.accounting import router; print('OK: Router carregat amb', len(router.routes), 'endpoints')"
```

Hauries de veure:
```
OK: Router carregat amb 15 endpoints
```

## Obtenir Logs Detallats

Si continues tenint errors, executa el servidor amb logs detallats:

```bash
python -m uvicorn app.interface.api.main:app --reload --log-level debug
```

Això mostrarà informació detallada sobre cada petició i error.
