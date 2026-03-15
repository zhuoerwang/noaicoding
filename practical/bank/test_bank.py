import pytest
from solution import BankSystem


# ── Level 1: Basic Account Operations ──────────────────────────────────


class TestLevel1:
    def test_open_account_returns_zero(self):
        bank = BankSystem()
        assert bank.open_account("Alice") == 0

    def test_open_account_auto_increments(self):
        bank = BankSystem()
        a0 = bank.open_account("Alice")
        a1 = bank.open_account("Bob")
        a2 = bank.open_account("Charlie")
        assert (a0, a1, a2) == (0, 1, 2)

    def test_deposit_increases_balance(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        bank.deposit(aid, 100.0)
        assert bank.get_balance(aid) == 100.0

    def test_multiple_deposits(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        bank.deposit(aid, 50.0)
        bank.deposit(aid, 25.0)
        assert bank.get_balance(aid) == 75.0

    def test_withdraw_decreases_balance(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        bank.deposit(aid, 100.0)
        bank.withdraw(aid, 40.0)
        assert bank.get_balance(aid) == 60.0

    def test_withdraw_insufficient_funds_raises(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        bank.deposit(aid, 50.0)
        with pytest.raises(ValueError):
            bank.withdraw(aid, 100.0)

    def test_withdraw_exact_balance(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        bank.deposit(aid, 100.0)
        bank.withdraw(aid, 100.0)
        assert bank.get_balance(aid) == 0.0

    def test_deposit_invalid_account_raises(self):
        bank = BankSystem()
        with pytest.raises(ValueError):
            bank.deposit(999, 50.0)

    def test_withdraw_invalid_account_raises(self):
        bank = BankSystem()
        with pytest.raises(ValueError):
            bank.withdraw(999, 50.0)

    def test_get_balance_invalid_account_raises(self):
        bank = BankSystem()
        with pytest.raises(ValueError):
            bank.get_balance(999)

    def test_new_account_has_zero_balance(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        assert bank.get_balance(aid) == 0.0

    def test_multiple_accounts_independent(self):
        bank = BankSystem()
        a = bank.open_account("Alice")
        b = bank.open_account("Bob")
        bank.deposit(a, 100.0)
        bank.deposit(b, 200.0)
        assert bank.get_balance(a) == 100.0
        assert bank.get_balance(b) == 200.0


# ── Level 2: Tellers ──────────────────────────────────────────────────


class TestLevel2:
    def test_add_teller(self):
        bank = BankSystem()
        bank.add_teller("T1")  # should not raise

    def test_add_duplicate_teller_raises(self):
        bank = BankSystem()
        bank.add_teller("T1")
        with pytest.raises(ValueError):
            bank.add_teller("T1")

    def test_deposit_with_teller(self):
        bank = BankSystem()
        bank.add_teller("T1")
        aid = bank.open_account("Alice")
        bank.deposit(aid, 100.0, teller_id="T1")
        assert bank.get_balance(aid) == 100.0

    def test_withdraw_with_teller(self):
        bank = BankSystem()
        bank.add_teller("T1")
        aid = bank.open_account("Alice")
        bank.deposit(aid, 100.0, teller_id="T1")
        bank.withdraw(aid, 30.0, teller_id="T1")
        assert bank.get_balance(aid) == 70.0

    def test_deposit_unregistered_teller_raises(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        with pytest.raises(ValueError):
            bank.deposit(aid, 100.0, teller_id="UNKNOWN")

    def test_withdraw_unregistered_teller_raises(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        bank.deposit(aid, 100.0)
        with pytest.raises(ValueError):
            bank.withdraw(aid, 50.0, teller_id="UNKNOWN")

    def test_transaction_history_records_open(self):
        bank = BankSystem()
        bank.open_account("Alice")
        history = bank.get_transaction_history()
        assert len(history) == 1
        assert history[0]["type"] == "open_account"
        assert history[0]["account_id"] == 0
        assert history[0]["teller_id"] is None
        assert history[0]["amount"] is None

    def test_transaction_history_records_deposit(self):
        bank = BankSystem()
        bank.add_teller("T1")
        aid = bank.open_account("Alice")
        bank.deposit(aid, 50.0, teller_id="T1")
        history = bank.get_transaction_history()
        dep = history[1]
        assert dep["type"] == "deposit"
        assert dep["teller_id"] == "T1"
        assert dep["amount"] == 50.0

    def test_transaction_history_records_withdrawal(self):
        bank = BankSystem()
        bank.add_teller("T1")
        aid = bank.open_account("Alice")
        bank.deposit(aid, 100.0, teller_id="T1")
        bank.withdraw(aid, 25.0, teller_id="T1")
        history = bank.get_transaction_history()
        wd = history[2]
        assert wd["type"] == "withdrawal"
        assert wd["amount"] == 25.0

    def test_transaction_history_ordering(self):
        bank = BankSystem()
        bank.add_teller("T1")
        a = bank.open_account("Alice")
        bank.deposit(a, 100.0, teller_id="T1")
        bank.withdraw(a, 10.0, teller_id="T1")
        history = bank.get_transaction_history()
        types = [t["type"] for t in history]
        assert types == ["open_account", "deposit", "withdrawal"]

    def test_transaction_history_is_copy(self):
        bank = BankSystem()
        bank.open_account("Alice")
        h1 = bank.get_transaction_history()
        h1.clear()
        h2 = bank.get_transaction_history()
        assert len(h2) == 1

    def test_multiple_tellers(self):
        bank = BankSystem()
        bank.add_teller("T1")
        bank.add_teller("T2")
        aid = bank.open_account("Alice")
        bank.deposit(aid, 50.0, teller_id="T1")
        bank.deposit(aid, 30.0, teller_id="T2")
        assert bank.get_balance(aid) == 80.0
        history = bank.get_transaction_history()
        assert history[1]["teller_id"] == "T1"
        assert history[2]["teller_id"] == "T2"


# ── Level 3: Branches ─────────────────────────────────────────────────


class TestLevel3:
    def test_add_branch(self):
        bank = BankSystem()
        bank.add_branch("B1", "123 Main St", 10000.0)

    def test_add_duplicate_branch_raises(self):
        bank = BankSystem()
        bank.add_branch("B1", "123 Main St", 10000.0)
        with pytest.raises(ValueError):
            bank.add_branch("B1", "456 Oak Ave", 5000.0)

    def test_branch_deposit_increases_balance_and_cash(self):
        bank = BankSystem()
        bank.add_branch("B1", "123 Main St", 10000.0)
        aid = bank.open_account("Alice")
        bank.branch_deposit("B1", aid, 500.0)
        assert bank.get_balance(aid) == 500.0

    def test_branch_withdraw_decreases_balance_and_cash(self):
        bank = BankSystem()
        bank.add_branch("B1", "123 Main St", 10000.0)
        aid = bank.open_account("Alice")
        bank.branch_deposit("B1", aid, 500.0)
        bank.branch_withdraw("B1", aid, 200.0)
        assert bank.get_balance(aid) == 300.0

    def test_branch_withdraw_insufficient_branch_cash_raises(self):
        bank = BankSystem()
        bank.add_branch("B1", "123 Main St", 100.0)
        aid = bank.open_account("Alice")
        bank.branch_deposit("B1", aid, 500.0)
        # Branch now has 600, account has 500. Try to withdraw more than branch has? No.
        # Make a scenario: branch has 100 initial + 500 deposit = 600
        # Need another scenario: small branch cash
        bank2 = BankSystem()
        bank2.add_branch("B1", "addr", 50.0)
        aid2 = bank2.open_account("Alice")
        bank2.branch_deposit("B1", aid2, 200.0)  # branch cash = 250, account = 200
        # Withdraw 260: account has 200 < 260 -> insufficient funds first
        # Better: deposit directly to get account balance up
        bank2.deposit(aid2, 500.0)  # account = 700, branch cash still 250
        with pytest.raises(ValueError):
            bank2.branch_withdraw("B1", aid2, 300.0)  # branch only has 250

    def test_branch_withdraw_insufficient_account_funds_raises(self):
        bank = BankSystem()
        bank.add_branch("B1", "123 Main St", 10000.0)
        aid = bank.open_account("Alice")
        bank.branch_deposit("B1", aid, 100.0)
        with pytest.raises(ValueError):
            bank.branch_withdraw("B1", aid, 200.0)

    def test_branch_deposit_invalid_branch_raises(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        with pytest.raises(ValueError):
            bank.branch_deposit("NOPE", aid, 100.0)

    def test_branch_withdraw_invalid_branch_raises(self):
        bank = BankSystem()
        aid = bank.open_account("Alice")
        bank.deposit(aid, 500.0)
        with pytest.raises(ValueError):
            bank.branch_withdraw("NOPE", aid, 100.0)

    def test_transfer_moves_funds(self):
        bank = BankSystem()
        a = bank.open_account("Alice")
        b = bank.open_account("Bob")
        bank.deposit(a, 300.0)
        bank.transfer(a, b, 100.0)
        assert bank.get_balance(a) == 200.0
        assert bank.get_balance(b) == 100.0

    def test_transfer_insufficient_funds_raises(self):
        bank = BankSystem()
        a = bank.open_account("Alice")
        b = bank.open_account("Bob")
        bank.deposit(a, 50.0)
        with pytest.raises(ValueError):
            bank.transfer(a, b, 100.0)

    def test_transfer_invalid_account_raises(self):
        bank = BankSystem()
        a = bank.open_account("Alice")
        bank.deposit(a, 100.0)
        with pytest.raises(ValueError):
            bank.transfer(a, 999, 50.0)

    def test_transfer_records_transactions(self):
        bank = BankSystem()
        a = bank.open_account("Alice")
        b = bank.open_account("Bob")
        bank.deposit(a, 300.0)
        bank.transfer(a, b, 100.0)
        history = bank.get_transaction_history()
        # open, open, deposit, withdrawal (transfer out), deposit (transfer in)
        assert len(history) == 5
        assert history[3]["type"] == "withdrawal"
        assert history[4]["type"] == "deposit"


# ── Level 4: HQ Settlement & Reporting ─────────────────────────────────


class TestLevel4:
    def _setup_bank(self) -> BankSystem:
        bank = BankSystem()
        bank.add_branch("B1", "123 Main St", 10000.0)
        bank.add_branch("B2", "456 Oak Ave", 5000.0)
        a = bank.open_account("Alice")
        b = bank.open_account("Bob")
        c = bank.open_account("Charlie")
        bank.branch_deposit("B1", a, 1000.0)
        bank.branch_deposit("B2", b, 2000.0)
        bank.branch_deposit("B1", c, 500.0)
        return bank

    def test_collect_cash_returns_total(self):
        bank = self._setup_bank()
        # B1: 10000+1000+500=11500, B2: 5000+2000=7000
        collected = bank.collect_cash(0.5)
        assert collected == pytest.approx(9250.0)

    def test_collect_cash_reduces_branch_cash(self):
        bank = self._setup_bank()
        bank.collect_cash(0.5)
        balances = bank.get_branch_balances()
        assert balances["B1"] == pytest.approx(5750.0)
        assert balances["B2"] == pytest.approx(3500.0)

    def test_collect_cash_increases_hq_reserves(self):
        bank = self._setup_bank()
        bank.collect_cash(0.5)
        report = bank.generate_report()
        assert report["hq_reserves"] == pytest.approx(9250.0)

    def test_collect_cash_full_ratio(self):
        bank = self._setup_bank()
        collected = bank.collect_cash(1.0)
        balances = bank.get_branch_balances()
        assert balances["B1"] == pytest.approx(0.0)
        assert balances["B2"] == pytest.approx(0.0)
        assert collected == pytest.approx(18500.0)

    def test_collect_cash_zero_ratio(self):
        bank = self._setup_bank()
        collected = bank.collect_cash(0.0)
        assert collected == pytest.approx(0.0)

    def test_get_top_customers(self):
        bank = self._setup_bank()
        top = bank.get_top_customers(2)
        assert len(top) == 2
        assert top[0]["name"] == "Bob"
        assert top[0]["balance"] == 2000.0
        assert top[1]["name"] == "Alice"
        assert top[1]["balance"] == 1000.0

    def test_get_top_customers_all(self):
        bank = self._setup_bank()
        top = bank.get_top_customers(10)
        assert len(top) == 3

    def test_get_top_customers_includes_fields(self):
        bank = self._setup_bank()
        top = bank.get_top_customers(1)
        assert "account_id" in top[0]
        assert "name" in top[0]
        assert "balance" in top[0]

    def test_get_branch_balances(self):
        bank = self._setup_bank()
        balances = bank.get_branch_balances()
        assert "B1" in balances
        assert "B2" in balances
        assert balances["B1"] == pytest.approx(11500.0)
        assert balances["B2"] == pytest.approx(7000.0)

    def test_generate_report_keys(self):
        bank = self._setup_bank()
        report = bank.generate_report()
        expected_keys = {"total_accounts", "total_deposits", "total_withdrawals",
                         "total_branch_cash", "hq_reserves"}
        assert set(report.keys()) == expected_keys

    def test_generate_report_values(self):
        bank = self._setup_bank()
        report = bank.generate_report()
        assert report["total_accounts"] == 3
        assert report["total_deposits"] == pytest.approx(3500.0)
        assert report["total_withdrawals"] == pytest.approx(0.0)
        assert report["total_branch_cash"] == pytest.approx(18500.0)
        assert report["hq_reserves"] == pytest.approx(0.0)

    def test_generate_report_after_operations(self):
        bank = self._setup_bank()
        bank.branch_withdraw("B1", 0, 200.0)  # Alice withdraws 200
        bank.collect_cash(0.25)
        report = bank.generate_report()
        assert report["total_accounts"] == 3
        assert report["total_withdrawals"] == pytest.approx(200.0)
        # B1: 11500-200=11300, B2: 7000. After 25% collect: B1=8475, B2=5250
        assert report["total_branch_cash"] == pytest.approx(13725.0)
        assert report["hq_reserves"] == pytest.approx(4575.0)
