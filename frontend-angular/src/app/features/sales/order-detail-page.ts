import { CurrencyPipe, DatePipe, LowerCasePipe } from '@angular/common';
import { Component, effect, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { finalize, Observable } from 'rxjs';

import { CompanyContext } from '../../core/company-context';
import { ErpApi } from '../../core/erp-api';
import { SalesOrder } from '../../core/models';

@Component({
  selector: 'app-order-detail-page',
  imports: [CurrencyPipe, DatePipe, LowerCasePipe, RouterLink],
  templateUrl: './order-detail-page.html',
  styleUrl: './order-detail-page.scss'
})
export class OrderDetailPage {
  private readonly api = inject(ErpApi);
  private readonly route = inject(ActivatedRoute);
  protected readonly companyContext = inject(CompanyContext);
  protected readonly order = signal<SalesOrder | null>(null);
  protected readonly loading = signal(false);
  protected readonly actionRunning = signal(false);
  protected readonly error = signal<string | null>(null);
  private readonly orderId = this.route.snapshot.paramMap.get('orderId');

  constructor() {
    effect(() => {
      const companyId = this.companyContext.selectedId();
      if (companyId && this.orderId) {
        this.load(companyId, this.orderId);
      }
    });
  }

  protected runAction(action: 'confirm' | 'deliver' | 'cancel'): void {
    const companyId = this.companyContext.selectedId();
    if (!companyId || !this.orderId || this.actionRunning()) return;

    const request: Observable<SalesOrder> = {
      confirm: this.api.confirmOrder(companyId, this.orderId),
      deliver: this.api.deliverOrder(companyId, this.orderId),
      cancel: this.api.cancelOrder(companyId, this.orderId)
    }[action];

    this.actionRunning.set(true);
    this.error.set(null);
    request.pipe(finalize(() => this.actionRunning.set(false))).subscribe({
      next: (order) => this.order.set(order),
      error: () => this.error.set('No s’ha pogut completar l’acció sobre la comanda.')
    });
  }

  private load(companyId: string, orderId: string): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.getOrder(companyId, orderId)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (order) => this.order.set(order),
        error: () => this.error.set('No s’ha pogut carregar la comanda.')
      });
  }
}
