from datetime import datetime, timezone
from extensions import db


class CompletedSurvey(db.Model):
    __tablename__ = "completed_surveys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey("surveys.id"), nullable=False)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # A user may only complete a given survey once
    __table_args__ = (db.UniqueConstraint("user_id", "survey_id", name="uq_user_survey"),)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "survey_id": self.survey_id,
            "survey_title": self.survey.title if self.survey else None,
            "company": self.survey.company if self.survey else None,
            "reward": round(self.survey.reward, 2) if self.survey else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
