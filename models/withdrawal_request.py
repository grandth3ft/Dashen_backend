from datetime import datetime, timezone
from extensions import db


class WithdrawalRequest(db.Model):
    __tablename__ = "withdrawal_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)  # pending|approved|rejected
    requested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else None,
            "amount": round(self.amount, 2),
            "phone_number": self.phone_number,
            "status": self.status,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
        }
