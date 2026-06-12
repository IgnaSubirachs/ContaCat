create table company_module_licenses (
    id varchar(36) not null,
    company_id varchar(36) not null,
    module_key varchar(50) not null,
    is_enabled boolean not null default true,
    starts_at date null,
    expires_at date null,
    created_at timestamp null default current_timestamp,
    updated_at timestamp null default current_timestamp on update current_timestamp,
    constraint pk_company_module_licenses primary key (id),
    constraint fk_company_module_licenses_company foreign key (company_id) references companies (id),
    constraint uq_company_module_licenses_scope unique (company_id, module_key),
    constraint chk_company_module_license_dates check (expires_at is null or starts_at is null or expires_at >= starts_at)
);

create index ix_company_module_licenses_company on company_module_licenses (company_id);
create index ix_company_module_licenses_module on company_module_licenses (module_key);
