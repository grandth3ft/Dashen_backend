"""
Admin routes: users, surveys CRUD, completed surveys, withdrawal approvals.

Every route here is protected by @admin_required (role claim embedded
in the JWT at login time — see utils/decorators.py).
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from extensions import db
from models import User, Survey, Question, Option, CompletedSurvey, WithdrawalRequest, UpgradeRequest
from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------------------------

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard_stats():
    total_users = User.query.filter_by(role="user").count()
    total_surveys = Survey.query.count()
    pending_withdrawals = WithdrawalRequest.query.filter_by(status="pending").count()
    completed_surveys = CompletedSurvey.query.count()
    total_earnings_paid = db.session.query(db.func.sum(User.total_withdrawn)).scalar() or 0
    pending_upgrades = UpgradeRequest.query.filter(
        UpgradeRequest.status.in_(["pending", "payment_confirmed"])
    ).count()

    return jsonify({
        "total_users": total_users,
        "total_surveys": total_surveys,
        "pending_withdrawals": pending_withdrawals,
        "completed_surveys": completed_surveys,
        "total_earnings_paid": round(total_earnings_paid, 2),
        "pending_upgrades": pending_upgrades,
    }), 200


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    users = User.query.filter_by(role="user").order_by(User.created_at.desc()).all()
    return jsonify({"users": [u.to_dict(include_stats=True) for u in users]}), 200


# ---------------------------------------------------------------------------
# Surveys (CRUD)
# ---------------------------------------------------------------------------

def _apply_questions(survey, questions_data):
    """Replaces a survey's question set. Used on create and full edits."""
    for q in survey.questions:
        db.session.delete(q)
    db.session.flush()

    for q in questions_data or []:
        question = Question(
            survey_id=survey.id,
            question=q.get("question", "").strip(),
            question_type=q.get("question_type", "text"),
        )
        db.session.add(question)
        db.session.flush()
        for opt_text in q.get("options", []):
            if opt_text and opt_text.strip():
                db.session.add(Option(question_id=question.id, option_text=opt_text.strip()))


@admin_bp.route("/surveys", methods=["GET"])
@admin_required
def list_all_surveys():
    surveys = Survey.query.order_by(Survey.created_at.desc()).all()
    return jsonify({"surveys": [s.to_dict() for s in surveys]}), 200


@admin_bp.route("/surveys", methods=["POST"])
@admin_required
def create_survey():
    data = request.get_json(silent=True) or {}

    required = ["company", "title", "description", "reward", "estimated_time"]
    if any(not data.get(field) for field in required):
        return jsonify({"error": "company, title, description, reward and estimated_time are required"}), 400

    try:
        reward = float(data["reward"])
        estimated_time = int(data["estimated_time"])
    except (TypeError, ValueError):
        return jsonify({"error": "reward and estimated_time must be numbers"}), 400

    survey = Survey(
        company=data["company"].strip(),
        title=data["title"].strip(),
        description=data["description"].strip(),
        reward=reward,
        estimated_time=estimated_time,
        status=data.get("status", "active"),
    )
    db.session.add(survey)
    db.session.flush()

    _apply_questions(survey, data.get("questions", []))

    db.session.commit()
    return jsonify({"message": "Survey created successfully", "survey": survey.to_dict(include_questions=True)}), 201


@admin_bp.route("/surveys/<int:survey_id>", methods=["PUT"])
@admin_required
def update_survey(survey_id):
    survey = Survey.query.get(survey_id)
    if not survey:
        return jsonify({"error": "Survey not found"}), 404

    data = request.get_json(silent=True) or {}

    if "company" in data:
        survey.company = data["company"].strip()
    if "title" in data:
        survey.title = data["title"].strip()
    if "description" in data:
        survey.description = data["description"].strip()
    if "reward" in data:
        try:
            survey.reward = float(data["reward"])
        except (TypeError, ValueError):
            return jsonify({"error": "reward must be a number"}), 400
    if "estimated_time" in data:
        try:
            survey.estimated_time = int(data["estimated_time"])
        except (TypeError, ValueError):
            return jsonify({"error": "estimated_time must be a number"}), 400
    if "status" in data and data["status"] in ("active", "inactive"):
        survey.status = data["status"]
    if "questions" in data:
        _apply_questions(survey, data["questions"])

    db.session.commit()
    return jsonify({"message": "Survey updated successfully", "survey": survey.to_dict(include_questions=True)}), 200


@admin_bp.route("/surveys/<int:survey_id>", methods=["DELETE"])
@admin_required
def delete_survey(survey_id):
    survey = Survey.query.get(survey_id)
    if not survey:
        return jsonify({"error": "Survey not found"}), 404

    db.session.delete(survey)
    db.session.commit()
    return jsonify({"message": "Survey deleted successfully"}), 200


# ---------------------------------------------------------------------------
# Completed surveys
# ---------------------------------------------------------------------------

@admin_bp.route("/completed", methods=["GET"])
@admin_required
def list_completed_surveys():
    completions = CompletedSurvey.query.order_by(CompletedSurvey.completed_at.desc()).all()
    results = []
    for c in completions:
        d = c.to_dict()
        d["user_name"] = c.user.full_name if c.user else None
        d["user_email"] = c.user.email if c.user else None
        results.append(d)
    return jsonify({"completed_surveys": results}), 200


# ---------------------------------------------------------------------------
# Withdrawal requests
# ---------------------------------------------------------------------------

@admin_bp.route("/withdrawals", methods=["GET"])
@admin_required
def list_all_withdrawals():
    status_filter = request.args.get("status")
    query = WithdrawalRequest.query
    if status_filter in ("pending", "approved", "rejected"):
        query = query.filter_by(status=status_filter)
    withdrawals = query.order_by(WithdrawalRequest.requested_at.desc()).all()
    return jsonify({"withdrawals": [w.to_dict() for w in withdrawals]}), 200


@admin_bp.route("/withdrawals/<int:withdrawal_id>", methods=["PUT"])
@admin_required
def update_withdrawal(withdrawal_id):
    withdrawal = WithdrawalRequest.query.get(withdrawal_id)
    if not withdrawal:
        return jsonify({"error": "Withdrawal request not found"}), 404

    if withdrawal.status != "pending":
        return jsonify({"error": "This request has already been processed"}), 400

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in ("approved", "rejected"):
        return jsonify({"error": "status must be 'approved' or 'rejected'"}), 400

    if new_status == "approved":
        user = User.query.get(withdrawal.user_id)
        if withdrawal.amount > user.wallet_balance:
            return jsonify({"error": "User's wallet balance is insufficient for this withdrawal"}), 400
        user.wallet_balance -= withdrawal.amount
        user.total_withdrawn += withdrawal.amount

    withdrawal.status = new_status
    db.session.commit()

    return jsonify({"message": f"Withdrawal {new_status}", "withdrawal": withdrawal.to_dict()}), 200


# ---------------------------------------------------------------------------
# Tier upgrade requests
# ---------------------------------------------------------------------------

@admin_bp.route("/upgrades", methods=["GET"])
@admin_required
def list_upgrade_requests():
    status_filter = request.args.get("status")
    query = UpgradeRequest.query
    if status_filter in ("pending", "payment_confirmed", "approved", "rejected"):
        query = query.filter_by(status=status_filter)
    upgrades = query.order_by(UpgradeRequest.requested_at.desc()).all()
    return jsonify({"upgrade_requests": [u.to_dict() for u in upgrades]}), 200


@admin_bp.route("/upgrades/<int:upgrade_id>/confirm-payment", methods=["PUT"])
@admin_required
def confirm_upgrade_payment(upgrade_id):
    upgrade = UpgradeRequest.query.get(upgrade_id)
    if not upgrade:
        return jsonify({"error": "Upgrade request not found"}), 404

    if upgrade.status != "pending":
        return jsonify({"error": "This request has already had its payment reviewed"}), 400

    upgrade.status = "payment_confirmed"
    db.session.commit()

    return jsonify({"message": "Payment confirmed. You can now approve or decline this upgrade.", "upgrade": upgrade.to_dict()}), 200


@admin_bp.route("/upgrades/<int:upgrade_id>", methods=["PUT"])
@admin_required
def review_upgrade_request(upgrade_id):
    upgrade = UpgradeRequest.query.get(upgrade_id)
    if not upgrade:
        return jsonify({"error": "Upgrade request not found"}), 404

    if upgrade.status != "payment_confirmed":
        return jsonify({"error": "Confirm the payment before approving or declining this request"}), 400

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in ("approved", "rejected"):
        return jsonify({"error": "status must be 'approved' or 'rejected'"}), 400

    if new_status == "approved":
        user = User.query.get(upgrade.user_id)
        user.tier = upgrade.tier_requested

    upgrade.status = new_status
    upgrade.reviewed_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({"message": f"Upgrade request {new_status}", "upgrade": upgrade.to_dict()}), 200
