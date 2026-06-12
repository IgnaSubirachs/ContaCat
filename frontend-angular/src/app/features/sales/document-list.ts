import { Directive, inject, signal } from '@angular/core';

import { CompanyContext } from '../../core/company-context';

@Directive()
export abstract class DocumentList<T> {
  protected readonly companyContext = inject(CompanyContext);
  protected readonly documents = signal<T[]>([]);
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);
}
