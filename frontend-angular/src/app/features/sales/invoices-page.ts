import { CurrencyPipe, DatePipe, LowerCasePipe } from '@angular/common';
import { Component, effect, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { ErpApi } from '../../core/erp-api';
import { SalesInvoice } from '../../core/models';
import { DocumentList } from './document-list';

@Component({
  selector: 'app-invoices-page',
  imports: [CurrencyPipe, DatePipe, LowerCasePipe, RouterLink],
  templateUrl: './invoices-page.html',
  styleUrl: './table-page.scss'
})
export class InvoicesPage extends DocumentList<SalesInvoice> {
  private readonly api = inject(ErpApi);

  constructor() {
    super();
    effect(() => {
      const companyId = this.companyContext.selectedId();
      if (companyId) this.load(companyId);
    });
  }

  protected load(companyId = this.companyContext.selectedId()): void {
    if (!companyId) return;
    this.loading.set(true);
    this.error.set(null);
    this.api.listInvoices(companyId)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (invoices) => this.documents.set(invoices),
        error: () => this.error.set('No s’han pogut carregar les factures.')
      });
  }

  protected statusLabel(status: SalesInvoice['status']): string {
    return { DRAFT: 'Esborrany', ISSUED: 'Emesa', PAID: 'Cobrada' }[status];
  }
}
