from app.infrastructure.db.base import init_db
from app.domain.accounts.services import AccountService
from app.domain.accounts.repositories import AccountRepository
from app.infrastructure.persistence.accounts.repository import SqlAlchemyAccountRepository
from app.interface.cli.menus import CliApp


def main():
    # 1) Crear taules si no existeixen
    init_db()

    # 2) Wiring de dependències
    account_repo: AccountRepository = SqlAlchemyAccountRepository()
    account_service = AccountService(account_repo)
    cli_app = CliApp(account_service)

    # 3) Arrencar CLI
    cli_app.run()


if __name__ == "__main__":
    main()
