class BankSystem:
    """
    Central banking system that manages accounts, tellers, branches, and HQ.
    Built incrementally across 4 levels.
    """

    def __init__(self) -> None:
        pass

    # ── Level 1: Basic Account Operations ──────────────────────────────

    def open_account(self, name: str) -> int:
        """Create a new account. Returns auto-incrementing account_id starting from 0."""
        raise NotImplementedError

    def deposit(self, account_id: int, amount: float, teller_id: str | None = None) -> None:
        """Deposit funds into an account.
        L1: teller_id is None.
        L2+: teller_id is required.
        """
        raise NotImplementedError

    def withdraw(self, account_id: int, amount: float, teller_id: str | None = None) -> None:
        """Withdraw funds from an account.
        Raises ValueError if account doesn't exist or insufficient funds.
        L1: teller_id is None.
        L2+: teller_id is required.
        """
        raise NotImplementedError

    def get_balance(self, account_id: int) -> float:
        """Return current balance for an account. Raises ValueError if invalid."""
        raise NotImplementedError

    # ── Level 2: Tellers ───────────────────────────────────────────────

    def add_teller(self, teller_id: str) -> None:
        """Register a teller. Raises ValueError if already exists."""
        raise NotImplementedError

    def get_transaction_history(self) -> list[dict]:
        """Return list of all transaction dicts."""
        raise NotImplementedError

    # ── Level 3: Branches ──────────────────────────────────────────────

    def add_branch(self, branch_id: str, address: str, initial_cash: float) -> None:
        """Register a branch. Raises ValueError if already exists."""
        raise NotImplementedError

    def branch_deposit(self, branch_id: str, account_id: int, amount: float) -> None:
        """Deposit at a specific branch. Increases branch cash on hand."""
        raise NotImplementedError

    def branch_withdraw(self, branch_id: str, account_id: int, amount: float) -> None:
        """Withdraw at a specific branch. Raises ValueError if branch lacks cash."""
        raise NotImplementedError

    def transfer(self, from_account: int, to_account: int, amount: float) -> None:
        """Transfer between accounts. No branch cash impact."""
        raise NotImplementedError

    # ── Level 4: HQ Settlement & Reporting ─────────────────────────────

    def collect_cash(self, ratio: float) -> float:
        """Collect fraction of each branch's cash to HQ. Returns total collected."""
        raise NotImplementedError

    def get_top_customers(self, n: int) -> list[dict]:
        """Top N customers by balance descending."""
        raise NotImplementedError

    def get_branch_balances(self) -> dict[str, float]:
        """Map branch_id -> cash_on_hand."""
        raise NotImplementedError

    def generate_report(self) -> dict:
        """Summary report of the entire bank system."""
        raise NotImplementedError
