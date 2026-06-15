alter table sales_invoices
    add column journal_entry_id varchar(36) null after sales_order_id,
    add constraint uq_sales_invoices_journal_entry unique (journal_entry_id),
    add constraint fk_sales_invoices_journal_entry foreign key (journal_entry_id) references journal_entries (id);
