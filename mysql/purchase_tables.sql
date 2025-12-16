-- Create Purchase Module tables

CREATE TABLE IF NOT EXISTS purchase_orders (
    id VARCHAR(36) PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_date DATE NOT NULL,
    partner_id VARCHAR(36) NOT NULL,
    status VARCHAR(20) NOT NULL,
    notes TEXT,
    subtotal DECIMAL(15,2),
    tax_amount DECIMAL(15,2),
    total_amount DECIMAL(15,2),
    INDEX idx_partner (partner_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_order_lines (
    id VARCHAR(36) PRIMARY KEY,
    purchase_order_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36),
    description TEXT NOT NULL,
    quantity DECIMAL(15,2) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 21.00,
    tax_amount DECIMAL(15,2),
    total DECIMAL(15,2),
    line_number INT DEFAULT 1,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
    INDEX idx_order (purchase_order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_invoices (
    id VARCHAR(36) PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_reference VARCHAR(100),
    invoice_date DATE NOT NULL,
    due_date DATE,
    partner_id VARCHAR(36) NOT NULL,
    purchase_order_id VARCHAR(36),
    status VARCHAR(20) NOT NULL,
    payment_status VARCHAR(20),
    notes TEXT,
    subtotal DECIMAL(15,2),
    tax_amount DECIMAL(15,2),
    total_amount DECIMAL(15,2),
    amount_paid DECIMAL(15,2) DEFAULT 0.00,
    journal_entry_id VARCHAR(36),
    INDEX idx_partner (partner_id),
    INDEX idx_status (status),
    INDEX idx_supplier_ref (supplier_reference)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS purchase_invoice_lines (
    id VARCHAR(36) PRIMARY KEY,
    purchase_invoice_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36),
    description TEXT NOT NULL,
    quantity DECIMAL(15,2) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 21.00,
    tax_amount DECIMAL(15,2),
    total DECIMAL(15,2),
    line_number INT DEFAULT 1,
    FOREIGN KEY (purchase_invoice_id) REFERENCES purchase_invoices(id) ON DELETE CASCADE,
    INDEX idx_invoice (purchase_invoice_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
