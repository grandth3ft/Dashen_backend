"""
Importing every model here ensures SQLAlchemy's metadata is fully
populated before db.create_all() runs in app.py -- otherwise tables
that are never imported elsewhere would silently not get created.
"""

from models.user import User
from models.survey import Survey
from models.question import Question
from models.option import Option
from models.completed_survey import CompletedSurvey
from models.withdrawal_request import WithdrawalRequest
from models.upgrade_request import UpgradeRequest

__all__ = [
    "User", "Survey", "Question", "Option",
    "CompletedSurvey", "WithdrawalRequest", "UpgradeRequest",
]
