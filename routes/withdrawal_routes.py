"""
Withdrawal routes: request + list withdrawals (user-facing).

Users now provide an amount and an M-Pesa phone number (no till number /
account name -- that pattern is only used for the tier upgrade payments,
see upgrade_routes.py). The minimum withdrawal amount is tier-based.
"""

import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import User, WithdrawalRequest

withdrawal_bp = Blueprint("withdrawal", __name__)

PHONE_REGEX = re.compile(r"^0[17]\d{8}$")  # e.g. 0712345678 or 0112345678


@withdrawal_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def request_withdrawal():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    data = request.get_json(silent=True) or {}
    amount = data.get("amount")
    phone_number = (data.get("phone_number") or "").strip()

    min_amount = user.tier_benefits["min_withdrawal"]

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "A valid withdrawal amount is required"}), 400

    if not PHONE_REGEX.match(phone_number):
        return jsonify({"error": "Enter a valid M-Pesa phone number, e.g. 0712345678"}), 400

    if amount < min_amount:
        return jsonify({
            "error": f"Minimum withdrawal on the {user.tier_benefits['label']} plan is KSh {min_amount:,.0f}. "
                     f"Upgrade your account to lower this threshold."
        }), 400

    # Account for money already tied up in other pending requests so the
    # user can't request more than they actually have available.
    pending_total = sum(
        w.amount for w in WithdrawalRequest.query.filter_by(user_id=user_id, status="pending").all()
    )
    available = user.wallet_balance - pending_total

    if amount > available:
        return jsonify({"error": "You cannot withdraw more than your available wallet balance"}), 400

    withdrawal = WithdrawalRequest(
        user_id=user_id,
        amount=amount,
        phone_number=phone_number,
        status="pending",
    )
    db.session.add(withdrawal)
    db.session.commit()

    return jsonify({
        "message": "Withdrawal request submitted. It is now pending admin approval.",
        "withdrawal": withdrawal.to_dict(),
    }), 201


@withdrawal_bp.route("/withdrawals", methods=["GET"])
@jwt_required()
def list_withdrawals():
    user_id = int(get_jwt_identity())
    withdrawals = (
        WithdrawalRequest.query.filter_by(user_id=user_id)
        .order_by(WithdrawalRequest.requested_at.desc())
        .all()
    )
    return jsonify({"withdrawals": [w.to_dict() for w in withdrawals]}), 200
