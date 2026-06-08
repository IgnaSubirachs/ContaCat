CREATE TABLE partners (
    id VARCHAR(36) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    name VARCHAR(200) NOT NULL,
    tax_id VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    is_supplier BOOLEAN NOT NULL DEFAULT FALSE,
    is_customer BOOLEAN NOT NULL DEFAULT FALSE,
    document_type VARCHAR(20) NOT NULL DEFAULT 'NIF',
    address_street VARCHAR(200) NOT NULL DEFAULT '',
    address_number VARCHAR(20) NOT NULL DEFAULT '',
    address_floor VARCHAR(50) NOT NULL DEFAULT '',
    postal_code VARCHAR(10) NOT NULL DEFAULT '',
    city VARCHAR(100) NOT NULL DEFAULT '',
    province VARCHAR(100) NOT NULL DEFAULT '',
    country VARCHAR(100) NOT NULL DEFAULT 'Espanya',
    vat_regime VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
    is_intra_eu BOOLEAN NOT NULL DEFAULT FALSE,
    eu_vat_number VARCHAR(30) NOT NULL DEFAULT '',
    iban VARCHAR(34) NOT NULL DEFAULT '',
    payment_method VARCHAR(50) NOT NULL DEFAULT 'TRANSFER',
    payment_days INT NOT NULL DEFAULT 30,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    CONSTRAINT fk_partners_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT uq_partners_company_tax_id UNIQUE (company_id, tax_id),
    CONSTRAINT chk_partners_payment_days CHECK (payment_days >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_partners_company_name ON partners(company_id, name);
CREATE INDEX ix_partners_company_customer ON partners(company_id, is_customer);
CREATE INDEX ix_partners_company_supplier ON partners(company_id, is_supplier);
