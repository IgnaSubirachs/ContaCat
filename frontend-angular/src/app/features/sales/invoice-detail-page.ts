import { CurrencyPipe, DatePipe, LowerCasePipe } from '@angular/common';
import { Component, effect, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { finalize, Observable } from 'rxjs';

import { CompanyContext } from '../../core/company-context';
import { ErpApi } from '../../core/erp-api';
import { SalesInvoice } from '../../core/models';

@Component({
  selector: 'app-invoice-detail-page',
  imports: [CurrencyPipe, DatePipe, LowerCasePipe, RouterLink],
  templateUrl: './invoice-detail-page.html',
  styleUrl: './order-detail-page.scss'
})
export class InvoiceDetailPage {
  private readonly api = inject(ErpApi);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  protected readonly companyContext = inject(CompanyContext);
  protected readonly invoice = signal<SalesInvoice | null>(null);
  protected readonly loading = signal(false);
  protected readonly actionRunning = signal(false);
  protected readonly error = signal<string | null>(null);
  private readonly invoiceId = this.route.snapshot.paramMap.get('invoiceId');

  constructor() {
    effect(() => {
      const companyId = this.companyContext.selectedId();
      if (companyId && this.invoiceId) this.load(companyId, this.invoiceId);
    });
  }

  protected runAction(action: 'issue' | 'paid'): void {
    const companyId = this.companyContext.selectedId();
    if (!companyId || !this.invoiceId || this.actionRunning()) return;

    const request: Observable<SalesInvoice> = action === 'issue'
      ? this.api.issueInvoice(companyId, this.invoiceId)
      : this.api.markInvoicePaid(companyId, this.invoiceId);
    this.actionRunning.set(true);
    this.error.set(null);
    request.pipe(finalize(() => this.actionRunning.set(false))).subscribe({
      next: (invoice) => this.invoice.set(invoice),
      error: () => this.error.set('No s’ha pogut completar l’acció sobre la factura.')
    });
  }

  protected deleteDraft(): void {
    const companyId = this.companyContext.selectedId();
    if (!companyId || !this.invoiceId || this.actionRunning()) return;

    this.actionRunning.set(true);
    this.error.set(null);
    this.api.deleteInvoiceDraft(companyId, this.invoiceId)
      .pipe(finalize(() => this.actionRunning.set(false)))
      .subscribe({
        next: () => void this.router.navigate(['/vendes/factures']),
        error: () => this.error.set('No s’ha pogut eliminar l’esborrany de factura.')
      });
  }

  protected statusLabel(status: SalesInvoice['status']): string {
    return { DRAFT: 'Esborrany', ISSUED: 'Emesa', PAID: 'Cobrada' }[status];
  }

  private load(companyId: string, invoiceId: string): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.getInvoice(companyId, invoiceId)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (invoice) => this.invoice.set(invoice),
        error: () => this.error.set('No s’ha pogut carregar la factura.')
      });
  }
}
