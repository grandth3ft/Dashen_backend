from datetime import datetime, timezone
from extensions import db
from config import TIER_CONFIG


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(255), nullable=False)  # bcrypt hash, never plaintext

    wallet_balance = db.Column(db.Float, default=0.0, nullable=False)
    total_earned = db.Column(db.Float, default=0.0, nullable=False)
    total_withdrawn = db.Column(db.Float, default=0.0, nullable=False)

    role = db.Column(db.String(20), default="user", nullable=False)  # "user" | "admin"
    tier = db.Column(db.String(20), default="free", nullable=False)  # "free" | "basic" | "premium" | "expert"
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    completed_surveys = db.relationship(
        "CompletedSurvey", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    withdrawal_requests = db.relationship(
        "WithdrawalRequest", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    upgrade_requests = db.relationship(
        "UpgradeRequest", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def tier_benefits(self):
        return TIER_CONFIG.get(self.tier, TIER_CONFIG["free"])

    def to_dict(self, include_stats=False):
        benefits = self.tier_benefits
        data = {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "wallet_balance": round(self.wallet_balance, 2),
            "total_earned": round(self.total_earned, 2),
            "total_withdrawn": round(self.total_withdrawn, 2),
            "role": self.role,
            "tier": self.tier,
            "tier_label": benefits["label"],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_stats:
            data["completed_surveys_count"] = len(self.completed_surveys)
            data["pending_withdrawals_count"] = len(
                [w for w in self.withdrawal_requests if w.status == "pending"]
            )
            data["min_withdrawal"] = benefits["min_withdrawal"]
            data["daily_survey_limit"] = benefits["daily_survey_limit"]
            data["reward_min"] = benefits["reward_min"]
            data["reward_max"] = benefits["reward_max"]
        return data
