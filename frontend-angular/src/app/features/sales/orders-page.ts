import { CurrencyPipe, DatePipe, LowerCasePipe } from '@angular/common';
import { Component, effect, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { ErpApi } from '../../core/erp-api';
import { SalesOrder } from '../../core/models';
import { DocumentList } from './document-list';

@Component({
  selector: 'app-orders-page',
  imports: [CurrencyPipe, DatePipe, LowerCasePipe, RouterLink],
  templateUrl: './orders-page.html',
  styleUrl: './table-page.scss'
})
export class OrdersPage extends DocumentList<SalesOrder> {
  private readonly api = inject(ErpApi);

  constructor() {
    super();
    effect(() => {
      const companyId = this.companyContext.selectedId();
      if (companyId) {
        this.load(companyId);
      }
    });
  }

  protected load(companyId = this.companyContext.selectedId()): void {
    if (!companyId) return;
    this.loading.set(true);
    this.api.listOrders(companyId)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (orders) => this.documents.set(orders),
        error: () => this.error.set('No s han pogut carregar les comandes.')
      });
  }
}
