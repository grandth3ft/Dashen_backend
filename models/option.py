from extensions import db


class Option(db.Model):
    __tablename__ = "options"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    option_text = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "option_text": self.option_text,
        }
