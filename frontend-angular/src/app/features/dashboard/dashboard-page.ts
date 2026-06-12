import { CurrencyPipe } from '@angular/common';
import { Component, computed, effect, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';

import { CompanyContext } from '../../core/company-context';
import { ErpApi } from '../../core/erp-api';
import { Quote, SalesOrder } from '../../core/models';

@Component({
  selector: 'app-dashboard-page',
  imports: [CurrencyPipe],
  templateUrl: './dashboard-page.html',
  styleUrl: './dashboard-page.scss'
})
export class DashboardPage {
  private readonly api = inject(ErpApi);
  protected readonly companyContext = inject(CompanyContext);
  protected readonly quotes = signal<Quote[]>([]);
  protected readonly orders = signal<SalesOrder[]>([]);
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly pipeline = computed(() => this.quotes().reduce((total, quote) => total + Number(quote.total), 0));
  protected readonly confirmedOrders = computed(() => this.orders().filter((order) => order.status === 'CONFIRMED').length);

  constructor() {
    effect(() => {
      const companyId = this.companyContext.selectedId();
      if (companyId) {
        this.refresh(companyId);
      }
    });
  }

  protected refresh(companyId = this.companyContext.selectedId()): void {
    if (!companyId) return;
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      quotes: this.api.listQuotes(companyId),
      orders: this.api.listOrders(companyId)
    }).subscribe({
      next: ({ quotes, orders }) => {
        this.quotes.set(quotes);
        this.orders.set(orders);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No s han pogut carregar els indicadors comercials.');
        this.loading.set(false);
      }
    });
  }
}
