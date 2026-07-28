"""
Lightweight, idempotent schema migrations for changes made after launch.

db.create_all() (called in app.py) only creates tables that don't exist
yet -- it never alters a table that's already there. Since Dashen Surveys
is already live with real data in Postgres, adding new columns or
renaming old ones needs an explicit, safe migration step.

Every migration here checks whether it's already been applied before
touching the database, so this is safe to run on every single boot,
against both a brand-new database and the live production one.
"""

from sqlalchemy import inspect, text
from extensions import db


def _table_exists(table):
    return table in inspect(db.engine).get_table_names()


def _column_exists(table, column):
    if not _table_exists(table):
        return False
    return column in [c["name"] for c in inspect(db.engine).get_columns(table)]


def run_migrations():
    is_postgres = db.engine.dialect.name == "postgresql"

    # 1. users.tier -- added for the Free / Basic / Premium / Expert tier system.
    if not _column_exists("users", "tier"):
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN tier VARCHAR(20) NOT NULL DEFAULT 'free'"))
            conn.commit()
        print("[migrate] Added users.tier (default 'free')")

    # 2. withdrawal_requests.till_number -> phone_number
    # (withdrawals now collect a phone number instead of a till number + account name)
    if _column_exists("withdrawal_requests", "till_number") and not _column_exists(
        "withdrawal_requests", "phone_number"
    ):
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE withdrawal_requests RENAME COLUMN till_number TO phone_number"))
            conn.commit()
        print("[migrate] Renamed withdrawal_requests.till_number -> phone_number")

    # 3. withdrawal_requests.account_name is no longer collected -- relax the
    # old NOT NULL constraint rather than dropping the column outright, so
    # this stays reversible and doesn't touch any existing historical data.
    if is_postgres and _column_exists("withdrawal_requests", "account_name"):
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE withdrawal_requests ALTER COLUMN account_name DROP NOT NULL"))
            conn.commit()
        print("[migrate] Relaxed withdrawal_requests.account_name to nullable")

    # Note: upgrade_requests is a brand-new table, so db.create_all() handles
    # creating it -- no migration needed for that one.
