"""
Central configuration for the Dashen Surveys backend.

Everything environment-specific lives here. To move from SQLite to
PostgreSQL later, only DATABASE_URL needs to change (in .env) — no
code changes required anywhere else in the app.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Database
    _raw_db_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database', 'dashen_surveys.db')}"
    )
    # Some providers (older Heroku-style URLs) still hand out "postgres://",
    # but SQLAlchemy 2.x requires the "postgresql://" scheme.
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["headers"]

    # CORS
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")


# ---------------------------------------------------------------------------
# Account tiers
# ---------------------------------------------------------------------------
# Single source of truth for tier benefits. Reward per completed survey is
# now tier-based (a random amount within the tier's range) rather than
# fixed per survey -- this keeps the incentive to upgrade simple and
# consistent regardless of which survey a user takes.
#
# Only "free", "basic", "premium", "expert" upgrade_cost values were
# specified directly; daily_survey_limit, reward ranges, and min_withdrawal
# for the paid tiers were derived to make each upgrade clearly worthwhile.
# Adjust freely -- this dict is the only place these numbers live.
TIER_CONFIG = {
    "free": {
        "label": "Free",
        "daily_survey_limit": 1,
        "reward_min": 40,
        "reward_max": 50,
        "min_withdrawal": 4500,
        "upgrade_cost": 0,
    },
    "basic": {
        "label": "Business Basic",
        "daily_survey_limit": 3,
        "reward_min": 60,
        "reward_max": 80,
        "min_withdrawal": 2000,
        "upgrade_cost": 400,
    },
    "premium": {
        "label": "Business Premium",
        "daily_survey_limit": 6,
        "reward_min": 90,
        "reward_max": 110,
        "min_withdrawal": 1000,
        "upgrade_cost": 800,
    },
    "expert": {
        "label": "Business Expert",
        "daily_survey_limit": None,  # None = unlimited
        "reward_min": 120,
        "reward_max": 150,
        "min_withdrawal": 300,
        "upgrade_cost": 1600,
    },
}

# The platform's M-Pesa Till Number users pay to when requesting an upgrade.
# Placeholder value -- replace with your real Till/Paybill number.
UPGRADE_TILL_NUMBER = "775566"
