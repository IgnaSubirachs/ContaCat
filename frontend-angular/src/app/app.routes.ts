import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./layout/erp-shell').then((module) => module.ErpShell),
    children: [
      {
        path: '',
        loadComponent: () => import('./features/dashboard/dashboard-page').then((module) => module.DashboardPage)
      },
      {
        path: 'vendes/pressupostos',
        loadComponent: () => import('./features/sales/quotes-page').then((module) => module.QuotesPage)
      },
      {
        path: 'vendes/comandes',
        loadComponent: () => import('./features/sales/orders-page').then((module) => module.OrdersPage)
      },
      { path: '**', redirectTo: '' }
    ]
  }
];
