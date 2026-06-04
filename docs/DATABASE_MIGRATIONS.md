# Migracions de Base de Dades

Aquest projecte passa a utilitzar Alembic com a font principal de canvis d'esquema.

## Comandes

```bash
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "descripcio_del_canvi"
```

Alembic llegeix `DATABASE_URL` des de `app.config`. Si no existeix, es fan servir les variables `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` i `DB_PASSWORD`.

## Taules core ERP

La revisio `20260604_0001` crea el nucli que tambe hauria de guiar la futura migracio a Java/Spring Boot:

- `companies`: empresa legal i futura base multiempresa.
- `warehouses`: magatzems per empresa.
- `products`: cataleg unic de productes i serveis.
- `tax_rates`: tipus fiscals configurables.
- `document_sequences`: numeracio transaccional per document, serie i exercici.

Les migracions antigues en SQL/Python es mantenen temporalment com a referencia historica, pero els nous canvis s'han de fer amb Alembic.
