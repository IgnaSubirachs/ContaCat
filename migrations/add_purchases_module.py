"""
Database migration to add Purchase module tables.
Run this script inside the Docker container after initial setup.
"""
import pymysql
import os

# Database configuration from environment or defaults
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "erpdb")

def run_migration():
    """Create purchase module tables."""
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    try:
        with connection.cursor() as cursor:
            print("Creating purchase_orders table...")
            cursor.execute("""
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
            """)
            
            print("Creating purchase_order_lines table...")
            cursor.execute("""
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
            """)
            
            print("Creating purchase_invoices table...")
            cursor.execute("""
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
            """)
            
            print("Creating purchase_invoice_lines table...")
            cursor.execute("""
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
            """)
            
            # Add SII settings columns if not exist
            print("Adding SII columns to company_settings...")
            cursor.execute("""
                ALTER TABLE company_settings 
                ADD COLUMN IF NOT EXISTS sii_enabled BOOLEAN DEFAULT 0,
                ADD COLUMN IF NOT EXISTS sii_test_mode BOOLEAN DEFAULT 1,
                ADD COLUMN IF NOT EXISTS sii_certificate_path VARCHAR(500),
                ADD COLUMN IF NOT EXISTS sii_certificate_password VARCHAR(500);
            """)
            
            connection.commit()
            print("\n✅ Migration completed successfully!")
            print("Purchase tables created:")
            print("  - purchase_orders")
            print("  - purchase_order_lines")
            print("  - purchase_invoices")
            print("  - purchase_invoice_lines")
            print("  - SII settings columns added")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    run_migration()
