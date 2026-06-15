create table sales_invoices (
    id varchar(36) not null,
    company_id varchar(36) not null,
    partner_id varchar(36) not null,
    sales_order_id varchar(36) not null,
    series varchar(20) null,
    fiscal_year int null,
    sequence_number int null,
    invoice_number varchar(50) null,
    invoice_date date not null,
    due_date date not null,
    status varchar(20) not null,
    notes text null,
    issued_at timestamp null,
    paid_at timestamp null,
    created_at timestamp null default current_timestamp,
    updated_at timestamp null default current_timestamp on update current_timestamp,
    constraint pk_sales_invoices primary key (id),
    constraint fk_sales_invoices_company foreign key (company_id) references companies (id),
    constraint fk_sales_invoices_partner foreign key (partner_id) references partners (id),
    constraint fk_sales_invoices_order foreign key (sales_order_id) references sales_orders (id),
    constraint uq_sales_invoices_order unique (sales_order_id),
    constraint uq_sales_invoices_company_number unique (company_id, invoice_number),
    constraint uq_sales_invoices_company_sequence unique (company_id, series, fiscal_year, sequence_number),
    constraint chk_sales_invoices_dates check (due_date >= invoice_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index ix_sales_invoices_company_date on sales_invoices (company_id, invoice_date);
create index ix_sales_invoices_company_status on sales_invoices (company_id, status);
create index ix_sales_invoices_partner on sales_invoices (partner_id);

create table sales_invoice_lines (
    id varchar(36) not null,
    sales_invoice_id varchar(36) not null,
    line_order int not null,
    product_code varchar(50) not null,
    description varchar(500) not null,
    quantity decimal(14, 3) not null,
    unit_price decimal(14, 2) not null,
    discount_percent decimal(5, 2) not null default 0,
    tax_rate decimal(5, 2) not null default 21,
    constraint pk_sales_invoice_lines primary key (id),
    constraint fk_sales_invoice_lines_invoice foreign key (sales_invoice_id) references sales_invoices (id),
    constraint uq_sales_invoice_lines_order unique (sales_invoice_id, line_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index ix_sales_invoice_lines_invoice on sales_invoice_lines (sales_invoice_id);
