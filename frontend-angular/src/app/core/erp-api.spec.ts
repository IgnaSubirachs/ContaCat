import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ErpApi } from './erp-api';

describe('ErpApi', () => {
  let api: ErpApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ErpApi, provideHttpClient(), provideHttpClientTesting()]
    });
    api = TestBed.inject(ErpApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('loads companies from the Spring Boot core API', () => {
    api.listCompanies().subscribe((companies) => expect(companies[0].name).toBe('ContaCAT Demo'));

    const request = http.expectOne('/api/core/companies');
    expect(request.request.method).toBe('GET');
    request.flush([{ id: 'company-1', name: 'ContaCAT Demo' }]);
  });

  it('scopes sales orders by company and status', () => {
    api.listOrders('company-1', 'CONFIRMED').subscribe();

    const request = http.expectOne('/api/sales/companies/company-1/orders?status=CONFIRMED');
    expect(request.request.method).toBe('GET');
    request.flush([]);
  });

  it('confirms an order through its business action endpoint', () => {
    api.confirmOrder('company-1', 'order-1').subscribe();

    const request = http.expectOne('/api/sales/companies/company-1/orders/order-1/confirm');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toBeNull();
    request.flush({ id: 'order-1', status: 'CONFIRMED' });
  });
});
