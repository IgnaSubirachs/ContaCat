import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { Company, Quote, SalesOrder } from './models';

@Injectable({ providedIn: 'root' })
export class ErpApi {
  private readonly http = inject(HttpClient);

  listCompanies() {
    return this.http.get<Company[]>('/api/core/companies');
  }

  listQuotes(companyId: string, status?: string) {
    const params = status ? new HttpParams().set('status', status) : undefined;
    return this.http.get<Quote[]>(`/api/sales/companies/${companyId}/quotes`, { params });
  }

  listOrders(companyId: string, status?: string) {
    const params = status ? new HttpParams().set('status', status) : undefined;
    return this.http.get<SalesOrder[]>(`/api/sales/companies/${companyId}/orders`, { params });
  }

  getOrder(companyId: string, orderId: string) {
    return this.http.get<SalesOrder>(`/api/sales/companies/${companyId}/orders/${orderId}`);
  }

  confirmOrder(companyId: string, orderId: string) {
    return this.http.post<SalesOrder>(`/api/sales/companies/${companyId}/orders/${orderId}/confirm`, null);
  }

  deliverOrder(companyId: string, orderId: string) {
    return this.http.post<SalesOrder>(`/api/sales/companies/${companyId}/orders/${orderId}/deliver`, null);
  }

  cancelOrder(companyId: string, orderId: string) {
    return this.http.post<SalesOrder>(`/api/sales/companies/${companyId}/orders/${orderId}/cancel`, null);
  }
}
