from dataclasses import dataclass
import json
import socket
from urllib.parse import urlparse
from urllib.request import urlopen

from sqlalchemy import text

from app.config import JAVA_ERP_BASE_URL
from app.infrastructure.db.base import SessionLocal


@dataclass
class ModuleStatus:
    name: str
    status: str
    detail: str
    url: str


def get_system_status() -> dict:
    database_ok, database_detail = _check_database()
    java_ok, java_detail = _check_java_backend()

    modules = [
        ModuleStatus("Clients i proveïdors", "operational" if database_ok else "unavailable", database_detail, "/partners/"),
        ModuleStatus("Vendes i compres", "operational" if database_ok else "unavailable", database_detail, "/sales/invoices/"),
        ModuleStatus("Bancs i tresoreria", "operational" if database_ok else "unavailable", database_detail, "/treasury/accounts"),
        ModuleStatus("Comptabilitat Java", "operational" if java_ok else "degraded", java_detail, "/accounting/"),
        ModuleStatus("Fiscalitat i informes", "operational" if database_ok else "unavailable", database_detail, "/fiscal/"),
        ModuleStatus("Inventari i actius", "operational" if database_ok else "unavailable", database_detail, "/inventory/"),
    ]
    operational = sum(module.status == "operational" for module in modules)
    overall = "operational" if operational == len(modules) else "degraded"
    return {
        "overall": overall,
        "operational_count": operational,
        "total_count": len(modules),
        "modules": modules,
        "database_ok": database_ok,
        "java_ok": java_ok,
    }


def _check_database() -> tuple[bool, str]:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return True, "Base de dades disponible"
    except Exception:
        return False, "No es pot connectar amb la base de dades"


def _check_java_backend() -> tuple[bool, str]:
    parsed = urlparse(JAVA_ERP_BASE_URL)
    host = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    try:
        with socket.create_connection((host, port), timeout=0.35):
            pass
    except OSError:
        return False, "Backend Java aturat; diari i informes comptables no estan disponibles"

    health_url = f"{JAVA_ERP_BASE_URL.rstrip('/')}/actuator/health"
    try:
        with urlopen(health_url, timeout=0.75) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("status") == "UP":
            return True, "Backend comptable disponible"
    except Exception:
        return False, "Backend Java respon per port pero no esta operatiu"

    return False, "Backend Java disponible pero amb estat no saludable"
