class BankSystem:
    """
    Central banking system that manages accounts, tellers, branches, and HQ.
    """

    def __init__(self) -> None:
        # L1
        self._accounts: dict[int, dict] = {}  # account_id -> {"name": str, "balance": float}
        self._next_account_id: int = 0
        self._transactions: list[dict] = []

        # L2
        self._tellers: set[str] = set()

        # L3
        self._branches: dict[str, dict] = {}  # branch_id -> {"address": str, "cash_on_hand": float}

        # L4
        self._hq_reserves: float = 0.0

    # ── Helpers ────────────────────────────────────────────────────────

    def _validate_account(self, account_id: int) -> None:
        if account_id not in self._accounts:
            raise ValueError(f"Account {account_id} does not exist")

    def _validate_teller(self, teller_id: str | None) -> None:
        if teller_id is not None and teller_id not in self._tellers:
            raise ValueError(f"Teller {teller_id} is not registered")

    def _validate_branch(self, branch_id: str) -> None:
        if branch_id not in self._branches:
            raise ValueError(f"Branch {branch_id} does not exist")

    def _record_transaction(
        self,
        txn_type: str,
        account_id: int,
        teller_id: str | None = None,
        amount: float | None = None,
    ) -> None:
        self._transactions.append({
            "type": txn_type,
            "account_id": account_id,
            "teller_id": teller_id,
            "amount": amount,
        })

    # ── Level 1: Basic Account Operations ──────────────────────────────

    def open_account(self, name: str) -> int:
        account_id = self._next_account_id
        self._next_account_id += 1
        self._accounts[account_id] = {"name": name, "balance": 0.0}
        self._record_transaction("open_account", account_id)
        return account_id

    def deposit(self, account_id: int, amount: float, teller_id: str | None = None) -> None:
        self._validate_account(account_id)
        self._validate_teller(teller_id)
        self._accounts[account_id]["balance"] += amount
        self._record_transaction("deposit", account_id, teller_id=teller_id, amount=amount)

    def withdraw(self, account_id: int, amount: float, teller_id: str | None = None) -> None:
        self._validate_account(account_id)
        self._validate_teller(teller_id)
        if self._accounts[account_id]["balance"] < amount:
            raise ValueError("Insufficient funds")
        self._accounts[account_id]["balance"] -= amount
        self._record_transaction("withdrawal", account_id, teller_id=teller_id, amount=amount)

    def get_balance(self, account_id: int) -> float:
        self._validate_account(account_id)
        return self._accounts[account_id]["balance"]

    # ── Level 2: Tellers ───────────────────────────────────────────────

    def add_teller(self, teller_id: str) -> None:
        if teller_id in self._tellers:
            raise ValueError(f"Teller {teller_id} already exists")
        self._tellers.add(teller_id)

    def get_transaction_history(self) -> list[dict]:
        return list(self._transactions)

    # ── Level 3: Branches ──────────────────────────────────────────────

    def add_branch(self, branch_id: str, address: str, initial_cash: float) -> None:
        if branch_id in self._branches:
            raise ValueError(f"Branch {branch_id} already exists")
        self._branches[branch_id] = {
            "address": address,
            "cash_on_hand": initial_cash,
        }

    def branch_deposit(self, branch_id: str, account_id: int, amount: float) -> None:
        self._validate_branch(branch_id)
        self._validate_account(account_id)
        self._accounts[account_id]["balance"] += amount
        self._branches[branch_id]["cash_on_hand"] += amount
        self._record_transaction("deposit", account_id, amount=amount)

    def branch_withdraw(self, branch_id: str, account_id: int, amount: float) -> None:
        self._validate_branch(branch_id)
        self._validate_account(account_id)
        if self._accounts[account_id]["balance"] < amount:
            raise ValueError("Insufficient funds")
        if self._branches[branch_id]["cash_on_hand"] < amount:
            raise ValueError(f"Branch {branch_id} does not have enough cash")
        self._accounts[account_id]["balance"] -= amount
        self._branches[branch_id]["cash_on_hand"] -= amount
        self._record_transaction("withdrawal", account_id, amount=amount)

    def transfer(self, from_account: int, to_account: int, amount: float) -> None:
        self._validate_account(from_account)
        self._validate_account(to_account)
        if self._accounts[from_account]["balance"] < amount:
            raise ValueError("Insufficient funds")
        self._accounts[from_account]["balance"] -= amount
        self._accounts[to_account]["balance"] += amount
        self._record_transaction("withdrawal", from_account, amount=amount)
        self._record_transaction("deposit", to_account, amount=amount)

    # ── Level 4: HQ Settlement & Reporting ─────────────────────────────

    def collect_cash(self, ratio: float) -> float:
        total_collected = 0.0
        for branch in self._branches.values():
            collected = branch["cash_on_hand"] * ratio
            branch["cash_on_hand"] -= collected
            total_collected += collected
        self._hq_reserves += total_collected
        return total_collected

    def get_top_customers(self, n: int) -> list[dict]:
        customers = [
            {"account_id": aid, "name": info["name"], "balance": info["balance"]}
            for aid, info in self._accounts.items()
        ]
        customers.sort(key=lambda c: c["balance"], reverse=True)
        return customers[:n]

    def get_branch_balances(self) -> dict[str, float]:
        return {bid: info["cash_on_hand"] for bid, info in self._branches.items()}

    def generate_report(self) -> dict:
        total_deposits = sum(
            t["amount"] for t in self._transactions
            if t["type"] == "deposit" and t["amount"] is not None
        )
        total_withdrawals = sum(
            t["amount"] for t in self._transactions
            if t["type"] == "withdrawal" and t["amount"] is not None
        )
        total_branch_cash = sum(
            info["cash_on_hand"] for info in self._branches.values()
        )
        return {
            "total_accounts": len(self._accounts),
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "total_branch_cash": total_branch_cash,
            "hq_reserves": self._hq_reserves,
        }
