import { computed, inject, Injectable, signal } from '@angular/core';
import { finalize } from 'rxjs';

import { ErpApi } from './erp-api';
import { Company } from './models';

@Injectable({ providedIn: 'root' })
export class CompanyContext {
  private readonly api = inject(ErpApi);
  readonly companies = signal<Company[]>([]);
  readonly selectedId = signal<string | null>(localStorage.getItem('contacat.companyId'));
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly selected = computed(() => this.companies().find((company) => company.id === this.selectedId()) ?? null);

  load(): void {
    if (this.loading() || this.companies().length) {
      return;
    }

    this.loading.set(true);
    this.api.listCompanies()
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (companies) => {
          this.companies.set(companies);
          if (!companies.some((company) => company.id === this.selectedId())) {
            this.select(companies[0]?.id ?? null);
          }
        },
        error: () => this.error.set('No es pot connectar amb el backend Spring Boot.')
      });
  }

  select(companyId: string | null): void {
    this.selectedId.set(companyId);
    if (companyId) {
      localStorage.setItem('contacat.companyId', companyId);
    } else {
      localStorage.removeItem('contacat.companyId');
    }
  }
}
