"""
DAY 1 · SESSION 2 — Advanced: Multi-file Understanding & Debugging
===================================================================
▶ DEMO SETUP: Open BOTH models/user.py AND this file in VS Code.
  Copilot sees the User dataclass and generates correct type-aware code.

▶ DEMO PROMPT for find_admins_by_domain:
  Delete the method body, keep only the comment:
  "# find all admin users whose email matches the given domain"
  Press Enter — Copilot completes with correct User attribute names.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from day1.session2_advanced.models.user import User


class UserService:
    def __init__(self, users: list[User]):
        self.users = users

    # ── Method 1 (multi-file demo) ────────────────────────────────────────
    # ▶ DEMO PROMPT: delete body → keep comment → Copilot completes
    # find all admin users whose email matches the given domain
    def find_admins_by_domain(self, domain: str) -> list[User]:
        return [
            u for u in self.users
            if u.role == "admin" and u.email.endswith(f"@{domain}")
        ]

    # ── Method 2 (debugging demo) ─────────────────────────────────────────
    # ▶ DEMO PROMPT: select paginate_v1 → Chat → "Why does this fail for page=1?"
    def paginate_v1(self, page: int, page_size: int = 3) -> list[User]:
        """BUGGY version — page 1 skips the first page_size items."""
        start = page * page_size      # Bug: page=1 gives start=3, misses first 3
        return self.users[start: start + page_size]

    # Copilot-fixed version:
    def paginate(self, page: int, page_size: int = 3) -> list[User]:
        """Return users for 1-indexed page."""
        start = (page - 1) * page_size
        return self.users[start: start + page_size]

    # ── Method 3 (optimization demo) ─────────────────────────────────────
    # ▶ DEMO PROMPT: select get_active_count_v1 → Chat →
    #   "Optimize: avoid iterating the list twice"
    def get_active_count_v1(self) -> dict:
        """Unoptimized: two passes over the list."""
        total  = len(self.users)
        active = len([u for u in self.users if u.active])
        return {"total": total, "active": active, "inactive": total - active}

    # Copilot suggests single-pass:
    def get_active_count(self) -> dict:
        """Optimized: single pass."""
        total = active = 0
        for u in self.users:
            total += 1
            if u.active:
                active += 1
        return {"total": total, "active": active, "inactive": total - active}


# ─────────────────────────────────────────────────────────────────────────────
# DEMO RUNNER
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from datetime import datetime

    users = [
        User("U1", "alice@acme.com",    "admin",  "Alice"),
        User("U2", "bob@acme.com",      "viewer", "Bob"),
        User("U3", "carol@techcorp.com","admin",  "Carol"),
        User("U4", "dave@acme.com",     "editor", "Dave"),
        User("U5", "eve@acme.com",      "admin",  "Eve"),
        User("U6", "frank@acme.com",    "viewer", "Frank", active=False),
    ]
    svc = UserService(users)

    print("=" * 60)
    print("DAY 1 · SESSION 2 — DEMO OUTPUT")
    print("=" * 60)

    print("\n[1] Multi-file: Admin users @acme.com")
    for u in svc.find_admins_by_domain("acme.com"):
        print(f"  {u}")

    print("\n[2] Debugging — Pagination bug")
    print(f"  paginate_v1(page=1): {svc.paginate_v1(1)}")  # skips first 3!
    print(f"  paginate(page=1):    {svc.paginate(1)}")      # correct

    print("\n[3] Optimization — Active count")
    print(f"  v1 (two-pass): {svc.get_active_count_v1()}")
    print(f"  v2 (one-pass): {svc.get_active_count()}")

    print("\n" + "=" * 60)
    print("Run tests:  pytest day1/session2_advanced/ -v")
    print("=" * 60)
