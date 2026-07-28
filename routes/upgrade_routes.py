"""
User-facing tier upgrade routes.

Flow: user picks a paid tier, sees the platform Till Number + amount to
pay, pays via M-Pesa outside the app, then clicks "Confirm Payment" --
which is what POST /upgrade/request represents. That creates a pending
UpgradeRequest for an admin to verify and approve (see admin_routes.py).
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import User, UpgradeRequest
from config import TIER_CONFIG, UPGRADE_TILL_NUMBER

upgrade_bp = Blueprint("upgrade", __name__)

TIER_ORDER = ["free", "basic", "premium", "expert"]
PAID_TIERS = ["basic", "premium", "expert"]


@upgrade_bp.route("/tiers", methods=["GET"])
@jwt_required()
def list_tiers():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    tiers = []
    for key in TIER_ORDER:
        benefits = TIER_CONFIG[key]
        tiers.append({
            "key": key,
            "label": benefits["label"],
            "daily_survey_limit": benefits["daily_survey_limit"],
            "reward_min": benefits["reward_min"],
            "reward_max": benefits["reward_max"],
            "min_withdrawal": benefits["min_withdrawal"],
            "upgrade_cost": benefits["upgrade_cost"],
        })

    return jsonify({
        "tiers": tiers,
        "current_tier": user.tier,
        "till_number": UPGRADE_TILL_NUMBER,
    }), 200


@upgrade_bp.route("/upgrade/request", methods=["POST"])
@jwt_required()
def request_upgrade():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    data = request.get_json(silent=True) or {}
    tier_requested = data.get("tier")

    if tier_requested not in PAID_TIERS:
        return jsonify({"error": "tier must be one of: basic, premium, expert"}), 400

    if TIER_ORDER.index(tier_requested) <= TIER_ORDER.index(user.tier):
        return jsonify({"error": "You can only upgrade to a higher tier than your current one"}), 400

    existing_pending = UpgradeRequest.query.filter_by(user_id=user_id, status="pending").first()
    if existing_pending:
        return jsonify({"error": "You already have a pending upgrade request"}), 409

    existing_confirmed = UpgradeRequest.query.filter_by(user_id=user_id, status="payment_confirmed").first()
    if existing_confirmed:
        return jsonify({"error": "You have an upgrade request awaiting final approval"}), 409

    upgrade = UpgradeRequest(
        user_id=user_id,
        tier_requested=tier_requested,
        amount=TIER_CONFIG[tier_requested]["upgrade_cost"],
        till_number=UPGRADE_TILL_NUMBER,
        status="pending",
    )
    db.session.add(upgrade)
    db.session.commit()

    return jsonify({
        "message": "Upgrade request submitted. An admin will verify your payment shortly.",
        "upgrade": upgrade.to_dict(),
    }), 201


@upgrade_bp.route("/upgrade/requests", methods=["GET"])
@jwt_required()
def list_my_upgrade_requests():
    user_id = int(get_jwt_identity())
    requests_ = (
        UpgradeRequest.query.filter_by(user_id=user_id)
        .order_by(UpgradeRequest.requested_at.desc())
        .all()
    )
    return jsonify({"upgrade_requests": [u.to_dict() for u in requests_]}), 200
