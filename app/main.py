from app.domain.accounts.services import AccountService
from app.infrastructure.accounts.sqlalchemy_repository import SqlAlchemyAccountRepository
from app.infrastructure.db.base import init_db
from app.interface.cli.menus import CliApp


def main():
    # Infraestructura
    init_db()  # crea les taules si no existeixen
    account_repo = SqlAlchemyAccountRepository()

    # Domini / Application
    account_service = AccountService(repository=account_repo)

    # Interfície
    cli_app = CliApp(account_service=account_service)
    cli_app.run()


if __name__ == "__main__":
    main()
