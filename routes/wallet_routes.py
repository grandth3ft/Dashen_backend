"""
Wallet routes: balance + recent activity feed.

Recent activity merges completed surveys (+reward) and withdrawal
requests (-amount) into a single chronological feed, since that's
how the frontend Wallet page displays them.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import User, CompletedSurvey, WithdrawalRequest

wallet_bp = Blueprint("wallet", __name__)


@wallet_bp.route("/wallet", methods=["GET"])
@jwt_required()
def get_wallet():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    activity = []

    for cs in CompletedSurvey.query.filter_by(user_id=user_id).all():
        activity.append({
            "type": "earning",
            "label": f"Completed {cs.survey.company if cs.survey else 'Survey'}",
            "amount": round(cs.survey.reward, 2) if cs.survey else 0,
            "date": cs.completed_at.isoformat() if cs.completed_at else None,
        })

    for wr in WithdrawalRequest.query.filter_by(user_id=user_id).all():
        activity.append({
            "type": "withdrawal",
            "label": f"Withdrawal ({wr.status.capitalize()})",
            "amount": -round(wr.amount, 2),
            "date": wr.requested_at.isoformat() if wr.requested_at else None,
            "status": wr.status,
        })

    activity.sort(key=lambda a: a["date"] or "", reverse=True)

    return jsonify({
        "wallet_balance": round(user.wallet_balance, 2),
        "total_earned": round(user.total_earned, 2),
        "total_withdrawn": round(user.total_withdrawn, 2),
        "activity": activity,
    }), 200
