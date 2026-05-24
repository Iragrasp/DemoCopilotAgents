"""
Unit tests for Session 1 demos.
▶ DEMO PROMPT: open demo.py, select validate_email, open Copilot Chat, type /tests
   Copilot generates tests like these automatically.

Run:  pytest day1/session1_copilot_basics/test_demo.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from day1.session1_copilot_basics.demo import validate_email, parse_sales_csv, get_active_users


# ── validate_email ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("email,expected", [
    ("user@example.com",   True),
    ("name+tag@sub.io",    True),
    ("user.name@corp.co",  True),
    ("bad-email",          False),
    ("@nodomain.com",      False),
    ("user@.com",          False),
    ("user@com",           False),
    ("",                   False),
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected


# ── parse_sales_csv ───────────────────────────────────────────────────────────
def test_parse_sales_csv_returns_dict():
    result = parse_sales_csv("data/sales.csv")
    assert isinstance(result, dict)
    assert len(result) > 0


def test_parse_sales_csv_keys_are_year_month():
    result = parse_sales_csv("data/sales.csv")
    for key in result:
        assert len(key) == 7, f"Key {key!r} should be YYYY-MM"
        assert key[4] == "-"


def test_parse_sales_csv_values_are_positive_floats():
    result = parse_sales_csv("data/sales.csv")
    for month, total in result.items():
        assert total > 0, f"Revenue for {month} should be > 0"


# ── get_active_users ──────────────────────────────────────────────────────────
def test_get_active_users_returns_only_active():
    users = [{"name": "Alice", "active": True}, {"name": "Bob", "active": False}]
    assert get_active_users(users) == ["Alice"]


def test_get_active_users_all_inactive():
    users = [{"name": "X", "active": False}]
    assert get_active_users(users) == []


def test_get_active_users_all_active():
    users = [{"name": "A", "active": True}, {"name": "B", "active": True}]
    assert get_active_users(users) == ["A", "B"]
