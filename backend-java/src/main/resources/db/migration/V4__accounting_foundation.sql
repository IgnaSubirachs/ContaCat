CREATE TABLE accounts (
    id VARCHAR(36) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    account_group INT NOT NULL,
    parent_account_id VARCHAR(36) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    CONSTRAINT fk_accounts_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT fk_accounts_parent FOREIGN KEY (parent_account_id) REFERENCES accounts(id),
    CONSTRAINT uq_accounts_company_code UNIQUE (company_id, code),
    CONSTRAINT chk_accounts_group CHECK (account_group BETWEEN 1 AND 9)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_accounts_company_group ON accounts(company_id, account_group);

CREATE TABLE journal_entries (
    id VARCHAR(36) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    sequence_id VARCHAR(36) NOT NULL,
    entry_number INT NOT NULL,
    formatted_number VARCHAR(50) NOT NULL,
    entry_date DATE NOT NULL,
    description VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL,
    attachment_path VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    posted_at TIMESTAMP NULL,
    CONSTRAINT fk_journal_entries_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT fk_journal_entries_sequence FOREIGN KEY (sequence_id) REFERENCES document_sequences(id),
    CONSTRAINT uq_journal_entries_company_number UNIQUE (company_id, entry_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_journal_entries_company_date ON journal_entries(company_id, entry_date);
CREATE INDEX ix_journal_entries_company_status ON journal_entries(company_id, status);

CREATE TABLE journal_lines (
    id VARCHAR(36) PRIMARY KEY,
    journal_entry_id VARCHAR(36) NOT NULL,
    account_id VARCHAR(36) NOT NULL,
    line_order INT NOT NULL,
    debit DECIMAL(15, 2) NOT NULL DEFAULT 0,
    credit DECIMAL(15, 2) NOT NULL DEFAULT 0,
    description VARCHAR(500) NOT NULL DEFAULT '',
    CONSTRAINT fk_journal_lines_entry FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id),
    CONSTRAINT fk_journal_lines_account FOREIGN KEY (account_id) REFERENCES accounts(id),
    CONSTRAINT chk_journal_lines_debit CHECK (debit >= 0),
    CONSTRAINT chk_journal_lines_credit CHECK (credit >= 0),
    CONSTRAINT uq_journal_lines_entry_order UNIQUE (journal_entry_id, line_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_journal_lines_account ON journal_lines(account_id);
