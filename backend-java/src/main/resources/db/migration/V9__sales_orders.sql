create table sales_orders (
    id varchar(36) not null,
    company_id varchar(36) not null,
    partner_id varchar(36) not null,
    quote_id varchar(36) null,
    series varchar(20) not null,
    fiscal_year int not null,
    sequence_number int not null,
    order_number varchar(50) not null,
    order_date date not null,
    status varchar(20) not null,
    delivery_date date null,
    delivery_address varchar(500) null,
    notes text null,
    created_at timestamp null default current_timestamp,
    updated_at timestamp null default current_timestamp on update current_timestamp,
    constraint pk_sales_orders primary key (id),
    constraint fk_sales_orders_company foreign key (company_id) references companies (id),
    constraint fk_sales_orders_partner foreign key (partner_id) references partners (id),
    constraint fk_sales_orders_quote foreign key (quote_id) references quotes (id),
    constraint uq_sales_orders_company_number unique (company_id, order_number),
    constraint uq_sales_orders_company_sequence unique (company_id, series, fiscal_year, sequence_number)
);

create index ix_sales_orders_company_date on sales_orders (company_id, order_date);
create index ix_sales_orders_company_status on sales_orders (company_id, status);
create index ix_sales_orders_partner on sales_orders (partner_id);

create table sales_order_lines (
    id varchar(36) not null,
    sales_order_id varchar(36) not null,
    line_order int not null,
    product_code varchar(50) not null,
    description varchar(500) not null,
    quantity decimal(14, 3) not null,
    unit_price decimal(14, 2) not null,
    discount_percent decimal(5, 2) not null default 0,
    tax_rate decimal(5, 2) not null default 21,
    constraint pk_sales_order_lines primary key (id),
    constraint fk_sales_order_lines_order foreign key (sales_order_id) references sales_orders (id),
    constraint uq_sales_order_lines_order unique (sales_order_id, line_order)
);

create index ix_sales_order_lines_order on sales_order_lines (sales_order_id);

insert ignore into document_sequences (
    id,
    company_id,
    document_type,
    series,
    fiscal_year,
    prefix,
    next_number,
    padding,
    is_active
) values (
    '00000000-0000-0000-0000-000000000105',
    '00000000-0000-0000-0000-000000000001',
    'SALES_ORDER',
    'A',
    2026,
    'CV-2026-',
    1,
    5,
    true
);
