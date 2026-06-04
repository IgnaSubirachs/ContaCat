INSERT IGNORE INTO companies (
    id,
    name,
    legal_name,
    tax_id,
    country,
    currency,
    is_active
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'ContaCat Demo',
    'ContaCat Demo SL',
    'B12345678',
    'ES',
    'EUR',
    TRUE
);

INSERT IGNORE INTO document_sequences (
    id,
    company_id,
    document_type,
    series,
    fiscal_year,
    prefix,
    next_number,
    padding,
    is_active
) VALUES
(
    '00000000-0000-0000-0000-000000000101',
    '00000000-0000-0000-0000-000000000001',
    'SALES_INVOICE',
    'A',
    2026,
    'FV-2026-',
    1,
    5,
    TRUE
),
(
    '00000000-0000-0000-0000-000000000102',
    '00000000-0000-0000-0000-000000000001',
    'PURCHASE_INVOICE',
    'A',
    2026,
    'FC-2026-',
    1,
    5,
    TRUE
),
(
    '00000000-0000-0000-0000-000000000103',
    '00000000-0000-0000-0000-000000000001',
    'JOURNAL_ENTRY',
    'A',
    2026,
    'JE-2026-',
    1,
    5,
    TRUE
);
