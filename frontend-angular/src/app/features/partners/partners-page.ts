import { CurrencyPipe } from '@angular/common';
import { Component, effect, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';

import { CompanyContext } from '../../core/company-context';
import { ErpApi } from '../../core/erp-api';
import { Partner } from '../../core/models';

type PartnerRole = 'ALL' | 'CUSTOMER' | 'SUPPLIER';

@Component({
  selector: 'app-partners-page',
  imports: [CurrencyPipe],
  templateUrl: './partners-page.html',
  styleUrls: ['../sales/table-page.scss', './partners-page.scss']
})
export class PartnersPage {
  private readonly api = inject(ErpApi);
  protected readonly companyContext = inject(CompanyContext);
  protected readonly partners = signal<Partner[]>([]);
  protected readonly role = signal<PartnerRole>('ALL');
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);

  constructor() {
    effect(() => {
      const companyId = this.companyContext.selectedId();
      const role = this.role();
      if (companyId) this.load(companyId, role);
    });
  }

  protected selectRole(role: PartnerRole): void {
    this.role.set(role);
  }

  protected roleLabel(partner: Partner): string {
    if (partner.customer && partner.supplier) return 'Client i proveïdor';
    return partner.customer ? 'Client' : 'Proveïdor';
  }

  protected load(companyId = this.companyContext.selectedId(), role = this.role()): void {
    if (!companyId) return;
    this.loading.set(true);
    this.error.set(null);
    this.api.listPartners(companyId, role === 'ALL' ? undefined : role)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (partners) => this.partners.set(partners),
        error: () => this.error.set('No s’han pogut carregar els clients i proveïdors.')
      });
  }
}
