import { Component, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { CompanyContext } from '../core/company-context';

@Component({
  selector: 'app-erp-shell',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './erp-shell.html',
  styleUrl: './erp-shell.scss'
})
export class ErpShell {
  protected readonly companyContext = inject(CompanyContext);
  protected readonly menuOpen = signal(false);

  constructor() {
    this.companyContext.load();
  }
}
