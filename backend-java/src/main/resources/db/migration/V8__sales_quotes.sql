create table quotes (
    id varchar(36) not null,
    company_id varchar(36) not null,
    partner_id varchar(36) not null,
    series varchar(20) not null,
    fiscal_year int not null,
    sequence_number int not null,
    quote_number varchar(50) not null,
    quote_date date not null,
    valid_until date not null,
    status varchar(20) not null,
    notes text null,
    created_at timestamp null default current_timestamp,
    updated_at timestamp null default current_timestamp on update current_timestamp,
    constraint pk_quotes primary key (id),
    constraint fk_quotes_company foreign key (company_id) references companies (id),
    constraint fk_quotes_partner foreign key (partner_id) references partners (id),
    constraint uq_quotes_company_number unique (company_id, quote_number),
    constraint uq_quotes_company_sequence unique (company_id, series, fiscal_year, sequence_number),
    constraint chk_quotes_dates check (valid_until >= quote_date)
);

create index ix_quotes_company_date on quotes (company_id, quote_date);
create index ix_quotes_company_status on quotes (company_id, status);
create index ix_quotes_partner on quotes (partner_id);

create table quote_lines (
    id varchar(36) not null,
    quote_id varchar(36) not null,
    line_order int not null,
    product_code varchar(50) not null,
    description varchar(500) not null,
    quantity decimal(14, 3) not null,
    unit_price decimal(14, 2) not null,
    discount_percent decimal(5, 2) not null default 0,
    tax_rate decimal(5, 2) not null default 21,
    constraint pk_quote_lines primary key (id),
    constraint fk_quote_lines_quote foreign key (quote_id) references quotes (id),
    constraint uq_quote_lines_order unique (quote_id, line_order)
);

create index ix_quote_lines_quote on quote_lines (quote_id);

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
    '00000000-0000-0000-0000-000000000104',
    '00000000-0000-0000-0000-000000000001',
    'QUOTE',
    'A',
    2026,
    'PR-2026-',
    1,
    5,
    true
);
