from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any
from urllib import error, parse, request

from app.config import JAVA_ERP_BASE_URL, JAVA_ERP_COMPANY_ID, JAVA_ERP_TIMEOUT_SECONDS


class JavaErpClientError(Exception):
    pass


@dataclass
class JavaErpClient:
    base_url: str = JAVA_ERP_BASE_URL.rstrip("/")
    configured_company_id: str | None = JAVA_ERP_COMPANY_ID
    timeout_seconds: float = JAVA_ERP_TIMEOUT_SECONDS

    def list_companies(self) -> list[dict[str, Any]]:
        return self._get("/api/core/companies")

    def list_module_catalog(self) -> list[dict[str, Any]]:
        return self._get("/api/admin/modules/catalog")

    def list_company_module_licenses(self, company_id: str | None = None) -> list[dict[str, Any]]:
        resolved_company_id = company_id or self.resolve_company_id()
        return self._get(f"/api/admin/companies/{resolved_company_id}/module-licenses")

    def update_company_module_license(
        self,
        module_key: str,
        enabled: bool,
        company_id: str | None = None,
        starts_at: date | None = None,
        expires_at: date | None = None,
    ) -> dict[str, Any]:
        resolved_company_id = company_id or self.resolve_company_id()
        payload: dict[str, Any] = {
            "enabled": enabled,
            "startsAt": starts_at.isoformat() if starts_at is not None else None,
            "expiresAt": expires_at.isoformat() if expires_at is not None else None,
        }
        return self._put(f"/api/admin/companies/{resolved_company_id}/module-licenses/{module_key}", payload)

    def resolve_company_id(self) -> str:
        if self.configured_company_id:
            return self.configured_company_id

        companies = self.list_companies()
        if not companies:
            raise JavaErpClientError("El backend Java no te cap empresa disponible.")
        return companies[0]["id"]

    def list_accounts(self, group: int | None = None) -> list[dict[str, Any]]:
        params = {"group": group} if group is not None else None
        return self._get(self._company_path("/accounts"), params=params)

    def create_account(
        self,
        code: str,
        name: str,
        account_type: str,
        group: int,
        parent_account_id: str | None,
    ) -> dict[str, Any]:
        payload = {
            "code": code,
            "name": name,
            "accountType": account_type,
            "group": group,
            "parentAccountId": parent_account_id,
            "active": True,
        }
        return self._post(self._company_path("/accounts"), payload)

    def list_partners(self, role: str | None = None) -> list[dict[str, Any]]:
        params = {"role": role} if role is not None else None
        return self._get(self._company_path("/partners"), params=params)

    def get_partner(self, partner_id: str) -> dict[str, Any]:
        return self._get(self._company_path(f"/partners/{partner_id}"))

    def list_quotes(
        self,
        status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {}
        if status is not None:
            params["status"] = status
        if start_date is not None:
            params["startDate"] = start_date.isoformat()
        if end_date is not None:
            params["endDate"] = end_date.isoformat()
        return self._get(f"/api/sales/companies/{self.resolve_company_id()}/quotes", params=params or None)

    def get_quote(self, quote_id: str) -> dict[str, Any]:
        return self._get(f"/api/sales/companies/{self.resolve_company_id()}/quotes/{quote_id}")

    def create_quote(
        self,
        partner_id: str,
        quote_date: date,
        valid_until: date,
        lines: list[dict[str, Any]],
        notes: str = "",
        series: str = "A",
    ) -> dict[str, Any]:
        payload = {
            "partnerId": partner_id,
            "series": series,
            "quoteDate": quote_date.isoformat(),
            "validUntil": valid_until.isoformat(),
            "notes": notes,
            "lines": lines,
        }
        return self._post(f"/api/sales/companies/{self.resolve_company_id()}/quotes", payload)

    def send_quote(self, quote_id: str) -> dict[str, Any]:
        return self._post(f"/api/sales/companies/{self.resolve_company_id()}/quotes/{quote_id}/send", None)

    def accept_quote(self, quote_id: str) -> dict[str, Any]:
        return self._post(f"/api/sales/companies/{self.resolve_company_id()}/quotes/{quote_id}/accept", None)

    def reject_quote(self, quote_id: str) -> dict[str, Any]:
        return self._post(f"/api/sales/companies/{self.resolve_company_id()}/quotes/{quote_id}/reject", None)

    def delete_quote(self, quote_id: str) -> Any:
        return self._delete(f"/api/sales/companies/{self.resolve_company_id()}/quotes/{quote_id}")

    def list_sales_orders(self, status: str | None = None) -> list[dict[str, Any]]:
        params = {"status": status} if status is not None else None
        return self._get(f"/api/sales/companies/{self.resolve_company_id()}/orders", params=params)

    def get_sales_order(self, order_id: str) -> dict[str, Any]:
        return self._get(f"/api/sales/companies/{self.resolve_company_id()}/orders/{order_id}")

    def create_sales_order_from_quote(self, quote_id: str, order_date: date | None = None) -> dict[str, Any]:
        payload = None if order_date is None else {"orderDate": order_date.isoformat()}
        return self._post(f"/api/sales/companies/{self.resolve_company_id()}/orders/from-quote/{quote_id}", payload)

    def confirm_sales_order(self, order_id: str) -> dict[str, Any]:
        return self._post(f"/api/sales/companies/{self.resolve_company_id()}/orders/{order_id}/confirm", None)

    def deliver_sales_order(self, order_id: str) -> dict[str, Any]:
        return self._post(f"/api/sales/companies/{self.resolve_company_id()}/orders/{order_id}/deliver", None)

    def cancel_sales_order(self, order_id: str) -> dict[str, Any]:
        return self._post(f"/api/sales/companies/{self.resolve_company_id()}/orders/{order_id}/cancel", None)

    def list_journal_entries(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {}
        if start_date is not None:
            params["startDate"] = start_date.isoformat()
        if end_date is not None:
            params["endDate"] = end_date.isoformat()
        return self._get(self._company_path("/journal-entries"), params=params or None)

    def create_journal_entry(
        self,
        entry_date: date,
        description: str,
        lines: list[dict[str, Any]],
        attachment_path: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "entryDate": entry_date.isoformat(),
            "description": description,
            "attachmentPath": attachment_path,
            "lines": lines,
        }
        return self._post(self._company_path("/journal-entries"), payload)

    def post_journal_entry(self, entry_id: str) -> dict[str, Any]:
        return self._post(self._company_path(f"/journal-entries/{entry_id}/post"), None)

    def trial_balance(self, end_date: date | None = None) -> dict[str, Any]:
        params = {"endDate": end_date.isoformat()} if end_date is not None else None
        return self._get(self._company_path("/accounting/reports/trial-balance"), params=params)

    def ledger(
        self,
        account_code: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, Any]:
        params: dict[str, str] = {}
        if start_date is not None:
            params["startDate"] = start_date.isoformat()
        if end_date is not None:
            params["endDate"] = end_date.isoformat()
        return self._get(self._company_path(f"/accounting/reports/ledger/{account_code}"), params=params or None)

    def balance_sheet(self, end_date: date | None = None) -> dict[str, Any]:
        params = {"endDate": end_date.isoformat()} if end_date is not None else None
        return self._get(self._company_path("/accounting/reports/balance-sheet"), params=params)

    def profit_loss(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, Any]:
        params: dict[str, str] = {}
        if start_date is not None:
            params["startDate"] = start_date.isoformat()
        if end_date is not None:
            params["endDate"] = end_date.isoformat()
        return self._get(self._company_path("/accounting/reports/profit-loss"), params=params or None)

    def _company_path(self, suffix: str) -> str:
        return f"/api/core/companies/{self.resolve_company_id()}{suffix}"

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request_json("GET", path, params=params)

    def _post(self, path: str, payload: dict[str, Any] | None) -> Any:
        return self._request_json("POST", path, payload=payload)

    def _put(self, path: str, payload: dict[str, Any] | None) -> Any:
        return self._request_json("PUT", path, payload=payload)

    def _delete(self, path: str) -> Any:
        return self._request_json("DELETE", path)

    def _request_json(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        query = f"?{parse.urlencode(params)}" if params else ""
        url = f"{self.base_url}{path}{query}"
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"

        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                content = response.read().decode("utf-8")
                if not content:
                    return None
                return json.loads(content, parse_float=Decimal)
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            message = self._extract_error_message(body) or f"Error {exc.code} del backend Java."
            raise JavaErpClientError(message) from exc
        except error.URLError as exc:
            raise JavaErpClientError(
                f"No puc connectar amb el backend Java a {self.base_url}. Assegura que Spring Boot esta arrencat."
            ) from exc

    def _extract_error_message(self, body: str) -> str | None:
        if not body:
            return None
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return body.strip() or None

        if isinstance(payload, dict):
            for key in ("message", "detail", "error"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return None
