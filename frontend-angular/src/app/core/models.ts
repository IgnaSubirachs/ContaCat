export interface Company {
  id: string;
  name: string;
  legalName: string;
  taxId: string;
  country: string;
  currency: string;
  active: boolean;
}

export interface CommercialDocumentLine {
  lineOrder: number;
  productCode: string;
  description: string;
  quantity: number;
  unitPrice: number;
  discountPercent: number;
  taxRate: number;
  subtotal: number;
  taxAmount: number;
  total: number;
}

export interface Quote {
  id: string;
  companyId: string;
  partnerId: string;
  partnerName: string;
  quoteNumber: string;
  quoteDate: string;
  validUntil: string;
  status: string;
  subtotal: number;
  totalTax: number;
  total: number;
  lines: CommercialDocumentLine[];
}

export interface SalesOrder {
  id: string;
  companyId: string;
  partnerId: string;
  partnerName: string;
  quoteId: string | null;
  quoteNumber: string | null;
  orderNumber: string;
  orderDate: string;
  deliveryDate: string | null;
  status: string;
  subtotal: number;
  totalTax: number;
  total: number;
  lines: CommercialDocumentLine[];
}

export interface SalesInvoice {
  id: string;
  companyId: string;
  partnerId: string;
  partnerName: string;
  salesOrderId: string;
  salesOrderNumber: string;
  journalEntryId: string | null;
  journalEntryNumber: string | null;
  invoiceNumber: string | null;
  invoiceDate: string;
  dueDate: string;
  status: 'DRAFT' | 'ISSUED' | 'PAID';
  subtotal: number;
  totalTax: number;
  total: number;
  lines: CommercialDocumentLine[];
  issuedAt: string | null;
  paidAt: string | null;
}
