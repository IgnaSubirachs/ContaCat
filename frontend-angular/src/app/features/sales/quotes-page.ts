import { CurrencyPipe, DatePipe, LowerCasePipe } from '@angular/common';
import { Component, effect, inject } from '@angular/core';
import { finalize } from 'rxjs';

import { ErpApi } from '../../core/erp-api';
import { Quote } from '../../core/models';
import { DocumentList } from './document-list';

@Component({
  selector: 'app-quotes-page',
  imports: [CurrencyPipe, DatePipe, LowerCasePipe],
  templateUrl: './quotes-page.html',
  styleUrl: './table-page.scss'
})
export class QuotesPage extends DocumentList<Quote> {
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
    this.api.listQuotes(companyId)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (quotes) => this.documents.set(quotes),
        error: () => this.error.set('No s han pogut carregar els pressupostos.')
      });
  }
}
