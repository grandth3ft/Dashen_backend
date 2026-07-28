"""
Startup seeding.

seed_admin() is idempotent — safe to call on every app boot. It only
creates the default admin account if one doesn't already exist.

Survey seeding (10 companies, 10-20 questions each) is added in Phase 4.
"""

from extensions import db, bcrypt
from models import User

DEFAULT_ADMIN_EMAIL = "admin@dashensurveys.com"
DEFAULT_ADMIN_PASSWORD = "Admin@123"


def seed_admin():
    existing_admin = User.query.filter_by(role="admin").first()
    if existing_admin:
        return

    admin = User(
        full_name="Dashen Admin",
        email=DEFAULT_ADMIN_EMAIL,
        phone="0700000000",
        password=bcrypt.generate_password_hash(DEFAULT_ADMIN_PASSWORD).decode("utf-8"),
        role="admin",
    )
    db.session.add(admin)
    db.session.commit()
    print(f"[seed] Created default admin account -> {DEFAULT_ADMIN_EMAIL} / {DEFAULT_ADMIN_PASSWORD}")
