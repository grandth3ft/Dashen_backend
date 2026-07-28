from datetime import datetime, timezone
from extensions import db


class Survey(db.Model):
    __tablename__ = "surveys"

    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reward = db.Column(db.Float, nullable=False)
    estimated_time = db.Column(db.Integer, nullable=False)  # minutes
    status = db.Column(db.String(20), default="active", nullable=False)  # "active" | "inactive"
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    questions = db.relationship(
        "Question", backref="survey", lazy=True, cascade="all, delete-orphan",
        order_by="Question.id",
    )
    completions = db.relationship(
        "CompletedSurvey", backref="survey", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, include_questions=False, completed_by_user=False):
        data = {
            "id": self.id,
            "company": self.company,
            "title": self.title,
            "description": self.description,
            "reward": round(self.reward, 2),
            "estimated_time": self.estimated_time,
            "status": self.status,
            "question_count": len(self.questions),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_by_user": completed_by_user,
        }
        if include_questions:
            data["questions"] = [q.to_dict() for q in self.questions]
        return data
