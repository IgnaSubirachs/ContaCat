from app.domain.accounts.services import AccountService


class CliApp:
    def __init__(self, account_service: AccountService):
        self._account_service = account_service

    def run(self):
        while True:
            self._print_main_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                self._handle_create_account()
            elif choice == "2":
                self._handle_list_accounts()
            elif choice == "0":
                print("Bye.")
                break
            else:
                print("Invalid option.")

    @staticmethod
    def _print_main_menu():
        print("\n=== ERP Accounting (CLI) ===")
        print("1. Add account")
        print("2. List accounts")
        print("0. Exit")

    def _handle_create_account(self):
        print("\n--- New Account ---")
        code = input("Account code (e.g. 570, 4300001): ").strip()
        name = input("Account name: ").strip()
        print("Account type options: asset, liability, equity, income, expense")
        account_type = input("Account type: ").strip()

        try:
            self._account_service.create_account(code, name, account_type)
            print("Account created successfully.")
        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def _handle_list_accounts(self):
        accounts = self._account_service.get_chart_of_accounts()
        print("\n--- Chart of Accounts ---")
        if not accounts:
            print("No accounts yet.")
            return

        for acc in accounts:
            status = "ACTIVE" if acc.is_active else "INACTIVE"
            print(f"{acc.code:>8} | {acc.name:<30} | {acc.account_type:<8} | {status}")
