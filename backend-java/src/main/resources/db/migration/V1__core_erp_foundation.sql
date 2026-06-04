CREATE TABLE companies (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255) NOT NULL,
    tax_id VARCHAR(50) NOT NULL,
    country VARCHAR(2) NOT NULL DEFAULT 'ES',
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    CONSTRAINT uk_companies_tax_id UNIQUE (tax_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE warehouses (
    id VARCHAR(36) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_warehouses_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT uq_warehouses_company_code UNIQUE (company_id, code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    sku VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    product_type VARCHAR(20) NOT NULL DEFAULT 'GOOD',
    default_tax_code VARCHAR(20),
    sales_account_code VARCHAR(20),
    purchase_account_code VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_products_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT uq_products_company_sku UNIQUE (company_id, sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tax_rates (
    id VARCHAR(36) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    rate DECIMAL(5,2) NOT NULL,
    tax_type VARCHAR(20) NOT NULL DEFAULT 'VAT',
    input_account_code VARCHAR(20),
    output_account_code VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_tax_rates_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT uq_tax_rates_company_code UNIQUE (company_id, code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE document_sequences (
    id VARCHAR(36) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    series VARCHAR(20) NOT NULL DEFAULT 'A',
    fiscal_year INT NOT NULL,
    prefix VARCHAR(30) NOT NULL DEFAULT '',
    next_number INT NOT NULL DEFAULT 1,
    padding INT NOT NULL DEFAULT 5,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_document_sequences_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT uq_doc_seq_scope UNIQUE (company_id, document_type, series, fiscal_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
