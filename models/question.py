from extensions import db


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey("surveys.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    # "multiple_choice" | "yes_no" | "radio" | "text"
    question_type = db.Column(db.String(30), nullable=False)

    options = db.relationship(
        "Option", backref="question", lazy=True, cascade="all, delete-orphan",
        order_by="Option.id",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "survey_id": self.survey_id,
            "question": self.question,
            "question_type": self.question_type,
            "options": [o.to_dict() for o in self.options],
        }
