# Bank System Design

An ICF-style system design project inspired by NeetCode's Bank design.

## Overview

Design a banking system with accounts, tellers, branches, and headquarters.
The system is built incrementally across four levels.

## Level 1: Basic Bank System

Implement `BankSystem` with core account operations. No tellers required.

### Methods

- `open_account(name: str) -> int` — Create a new account. Returns an auto-incrementing account ID starting from 0. Records an "open_account" transaction.
- `deposit(account_id: int, amount: float) -> None` — Deposit funds into an account. Raises `ValueError` if account does not exist.
- `withdraw(account_id: int, amount: float) -> None` — Withdraw funds from an account. Raises `ValueError` if account does not exist or has insufficient funds.
- `get_balance(account_id: int) -> float` — Returns the current balance. Raises `ValueError` if account does not exist.

### Transaction Format

Each transaction is recorded as a dict:
```python
{
    "type": "deposit" | "withdrawal" | "open_account",
    "account_id": int,
    "teller_id": None,
    "amount": float | None  # None for open_account
}
```

## Level 2: Tellers

All deposits and withdrawals must now go through a registered teller.

### New/Modified Methods

- `add_teller(teller_id: str) -> None` — Register a teller. Raises `ValueError` if teller already exists.
- `deposit(account_id: int, teller_id: str, amount: float) -> None` — Deposit via a teller. Raises `ValueError` if teller is not registered.
- `withdraw(account_id: int, teller_id: str, amount: float) -> None` — Withdraw via a teller. Raises `ValueError` if teller is not registered.
- `get_transaction_history() -> list[dict]` — Returns a list of all transaction dicts, including teller_id.

## Level 3: Branches

Branches manage physical cash. Withdrawals are limited by branch cash on hand.

### New/Modified Methods

- `add_branch(branch_id: str, address: str, initial_cash: float) -> None` — Register a branch with an initial cash reserve. Raises `ValueError` if branch already exists.
- `branch_deposit(branch_id: str, account_id: int, amount: float) -> None` — Deposit at a specific branch. Increases the branch's cash on hand by the deposit amount. Uses the first available teller. Raises `ValueError` if branch does not exist.
- `branch_withdraw(branch_id: str, account_id: int, amount: float) -> None` — Withdraw at a specific branch. Decreases the branch's cash on hand. Raises `ValueError` if branch doesn't have enough cash or account has insufficient funds.
- `transfer(from_account: int, to_account: int, amount: float) -> None` — Transfer funds between two accounts. No branch cash impact. Raises `ValueError` if either account is invalid or insufficient funds.

## Level 4: HQ Settlement and Reporting

End-of-day operations for headquarters.

### New Methods

- `collect_cash(ratio: float) -> float` — Collect a fraction (0.0 to 1.0) of each branch's cash on hand and move it to HQ reserves. Returns total collected.
- `get_top_customers(n: int) -> list[dict]` — Return the top N customers sorted by balance (descending). Each entry: `{"account_id": int, "name": str, "balance": float}`.
- `get_branch_balances() -> dict[str, float]` — Return a dict mapping branch_id to cash_on_hand.
- `generate_report() -> dict` — Return a summary dict with keys: `"total_accounts"`, `"total_deposits"`, `"total_withdrawals"`, `"total_branch_cash"`, `"hq_reserves"`.

## Constraints

- No external dependencies (stdlib only).
- No randomness. All operations are deterministic.
- Account IDs auto-increment from 0.
- All monetary amounts are floats.
