from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domain.auth.dependencies import get_current_active_user
from app.infrastructure.java_erp_client import JavaErpClient, JavaErpClientError
from app.interface.api.templates import templates


def get_java_erp_client() -> JavaErpClient:
    return JavaErpClient()


router = APIRouter(
    prefix="/accounting",
    tags=["accounting"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_class=HTMLResponse)
async def accounting_home(request: Request):
    return templates.TemplateResponse("accounting/home.html", {"request": request})


@router.get("/journal", response_class=HTMLResponse)
async def journal_list(request: Request, client: JavaErpClient = Depends(get_java_erp_client)):
    try:
        entries = [_to_journal_entry_view(entry) for entry in client.list_journal_entries()]
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "accounting/journal.html",
        {"request": request, "entries": entries},
    )


@router.get("/journal/create", response_class=HTMLResponse)
async def create_entry_form(request: Request, client: JavaErpClient = Depends(get_java_erp_client)):
    try:
        accounts = [
            {"code": account["code"], "name": account["name"], "type": account["accountType"], "group": account["group"]}
            for account in client.list_accounts()
        ]
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "accounting/journal/create.html",
        {"request": request, "accounts": accounts},
    )


@router.post("/journal/create")
async def create_entry(
    request: Request,
    entry_date: date = Form(...),
    description: str = Form(...),
    attachment: UploadFile | None = File(None),
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        form_data = await request.form()
        lines = _parse_journal_lines(form_data)
        attachment_path = _store_attachment(attachment)
        client.create_journal_entry(entry_date, description, lines, attachment_path)
        return RedirectResponse(url="/accounting/journal", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/journal/{entry_id}/post")
async def post_entry(entry_id: str, client: JavaErpClient = Depends(get_java_erp_client)):
    try:
        client.post_journal_entry(entry_id)
        return RedirectResponse(url="/accounting/journal", status_code=303)
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/ledger/{account_code}", response_class=HTMLResponse)
async def account_ledger(
    request: Request,
    account_code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        ledger = client.ledger(account_code, _parse_iso_date(start_date), _parse_iso_date(end_date))
        return templates.TemplateResponse(
            "accounting/ledger.html",
            {"request": request, "ledger": _to_ledger_view(ledger)},
        )
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/reports/trial-balance", response_class=HTMLResponse)
async def trial_balance(
    request: Request,
    end_date: str | None = None,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        report = client.trial_balance(_parse_iso_date(end_date))
        return templates.TemplateResponse(
            "accounting/trial_balance.html",
            {"request": request, "trial_balance": _to_trial_balance_view(report)},
        )
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/reports/balance-sheet", response_class=HTMLResponse)
async def balance_sheet(
    request: Request,
    end_date: str | None = None,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        report = client.balance_sheet(_parse_iso_date(end_date))
        return templates.TemplateResponse(
            "accounting/balance_sheet.html",
            {"request": request, "balance_sheet": _to_balance_sheet_view(report)},
        )
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/reports/profit-loss", response_class=HTMLResponse)
async def profit_loss(
    request: Request,
    start_date: str | None = None,
    end_date: str | None = None,
    client: JavaErpClient = Depends(get_java_erp_client),
):
    try:
        report = client.profit_loss(_parse_iso_date(start_date), _parse_iso_date(end_date))
        return templates.TemplateResponse(
            "accounting/profit_loss.html",
            {"request": request, "profit_loss": _to_profit_loss_view(report)},
        )
    except JavaErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def _parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_journal_lines(form_data) -> list[dict]:
    lines: list[dict] = []
    index = 0

    while True:
        account_code = form_data.get(f"account_code_{index}") or form_data.get(f"account_{index}")
        debit_raw = form_data.get(f"debit_{index}")
        credit_raw = form_data.get(f"credit_{index}")
        description = form_data.get(f"description_{index}", "")

        if account_code:
            debit = Decimal(debit_raw or "0")
            credit = Decimal(credit_raw or "0")
            lines.append(
                {
                    "accountCode": account_code,
                    "debit": str(debit),
                    "credit": str(credit),
                    "description": description,
                }
            )

        if not account_code and debit_raw is None and credit_raw is None:
            break

        index += 1
        if index > 200:
            break

    if len(lines) < 2:
        raise JavaErpClientError("Cal informar almenys dues linies comptables.")

    total_debit = sum(Decimal(line["debit"]) for line in lines)
    total_credit = sum(Decimal(line["credit"]) for line in lines)
    if total_debit != total_credit:
        raise JavaErpClientError("El deure i l'haver han de quadrar abans de crear l'assentament.")

    return lines


def _store_attachment(attachment: UploadFile | None) -> str | None:
    if attachment is None or not attachment.filename:
        return None

    upload_dir = os.path.join("frontend", "static", "uploads", "accounting")
    os.makedirs(upload_dir, exist_ok=True)
    extension = os.path.splitext(attachment.filename)[1]
    filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(attachment.file, buffer)

    return f"/static/uploads/accounting/{filename}"


def _to_journal_entry_view(entry: dict) -> SimpleNamespace:
    lines = [_to_journal_line_view(line) for line in entry["lines"]]
    total_debit = sum(line.debit for line in lines)
    total_credit = sum(line.credit for line in lines)
    return SimpleNamespace(
        id=entry["id"],
        entry_number=entry["formattedNumber"],
        entry_date=_parse_date_value(entry["entryDate"]),
        description=entry["description"],
        status=SimpleNamespace(value=entry["status"]),
        lines=lines,
        total_debit=total_debit,
        total_credit=total_credit,
    )


def _to_journal_line_view(line: dict) -> SimpleNamespace:
    return SimpleNamespace(
        account_code=line["accountCode"],
        account_name=line["accountName"],
        description=line["description"] or "",
        debit=_to_decimal(line["debit"]),
        credit=_to_decimal(line["credit"]),
    )


def _to_trial_balance_view(report: dict) -> list[SimpleNamespace]:
    return [
        SimpleNamespace(
            code=line["accountCode"],
            name=line["accountName"],
            type=line["accountType"],
            balance=_to_decimal(line["balance"]),
        )
        for line in report["lines"]
    ]


def _to_ledger_view(report: dict) -> SimpleNamespace:
    return SimpleNamespace(
        account_code=report["accountCode"],
        account_name=report["accountName"],
        start_date=_parse_date_value(report["startDate"]),
        end_date=_parse_date_value(report["endDate"]),
        final_balance=_to_decimal(report["finalBalance"]),
        lines=[
            SimpleNamespace(
                entry_id=line["entryId"],
                entry_number=line["formattedNumber"],
                entry_date=_parse_date_value(line["entryDate"]),
                entry_description=line["entryDescription"],
                line_description=line["lineDescription"] or "",
                debit=_to_decimal(line["debit"]),
                credit=_to_decimal(line["credit"]),
                running_balance=_to_decimal(line["runningBalance"]),
            )
            for line in report["lines"]
        ],
    )


def _to_balance_sheet_view(report: dict) -> SimpleNamespace:
    actiu_total = _to_decimal(report["totalAssets"])
    passiu_total = _to_decimal(report["totalEquityAndLiabilities"])
    return SimpleNamespace(
        end_date=_parse_date_value(report["endDate"]),
        actiu=SimpleNamespace(
            no_corrent=_to_balance_section(report["nonCurrentAssets"]),
            corrent=_to_balance_section(report["currentAssets"]),
            total=actiu_total,
        ),
        patrimoni_net_i_passiu=SimpleNamespace(
            patrimoni_net=_to_balance_section(report["equity"]),
            passiu_no_corrent=_to_balance_section(report["nonCurrentLiabilities"]),
            passiu_corrent=_to_balance_section(report["currentLiabilities"]),
            total=passiu_total,
        ),
    )


def _to_balance_section(section: dict) -> SimpleNamespace:
    groups: dict[str, SimpleNamespace] = {}
    for group in section["groups"]:
        groups[group["name"]] = SimpleNamespace(
            total=_to_decimal(group["total"]),
            accounts=[
                SimpleNamespace(
                    code=line["code"],
                    name=line["name"],
                    balance=_to_decimal(line["balance"]),
                )
                for line in group["accounts"]
            ],
        )
    return SimpleNamespace(total=_to_decimal(section["total"]), groups=groups)


def _to_profit_loss_view(report: dict) -> SimpleNamespace:
    groups: dict[str, SimpleNamespace] = {}
    for group in report["groups"]:
        groups[group["name"]] = SimpleNamespace(
            total=_to_decimal(group["total"]),
            account_lines=[
                SimpleNamespace(
                    code=line["code"],
                    name=line["name"],
                    amount=_to_decimal(line["amount"]),
                )
                for line in group["lines"]
            ],
        )

    return SimpleNamespace(
        start_date=_parse_date_value(report["startDate"]),
        end_date=_parse_date_value(report["endDate"]),
        groups=groups,
        resultat_explotacio=_to_decimal(report["operatingResult"]),
        resultat_financer=_to_decimal(report["financialResult"]),
        resultat_abans_impostos=_to_decimal(report["resultBeforeTax"]),
        resultat_exercici=_to_decimal(report["resultForYear"]),
    )


def _parse_date_value(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.fromisoformat(value).date() if "T" in value else date.fromisoformat(value)


def _to_decimal(value: Decimal | int | float | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))
