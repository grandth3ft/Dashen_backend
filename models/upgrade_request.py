from datetime import datetime, timezone
from extensions import db


class UpgradeRequest(db.Model):
    """
    A user's claim to have paid the Till Number for a tier upgrade.

    Status flow: pending -> payment_confirmed -> approved | rejected
    - pending: user submitted the request, nothing verified yet
    - payment_confirmed: admin has checked the M-Pesa statement and confirmed
      the money arrived, but hasn't finalized the tier change yet
    - approved: admin granted the tier upgrade (User.tier is updated)
    - rejected: admin declined (no wallet/tier changes)
    """

    __tablename__ = "upgrade_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tier_requested = db.Column(db.String(20), nullable=False)  # basic | premium | expert
    amount = db.Column(db.Float, nullable=False)
    till_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    requested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else None,
            "user_email": self.user.email if self.user else None,
            "tier_requested": self.tier_requested,
            "amount": round(self.amount, 2),
            "till_number": self.till_number,
            "status": self.status,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
