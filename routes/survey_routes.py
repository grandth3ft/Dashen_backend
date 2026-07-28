"""
Survey routes: list, detail, submit.

Reward is now tier-based: a random amount within the user's tier range,
credited regardless of which survey they take (see config.TIER_CONFIG).
Submission also enforces each tier's daily survey limit server-side --
the frontend shows/blocks this too, but the real enforcement lives here.
"""

import random
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Survey, CompletedSurvey, User

survey_bp = Blueprint("survey", __name__)


def _start_of_today_utc():
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _surveys_completed_today(user_id):
    return CompletedSurvey.query.filter(
        CompletedSurvey.user_id == user_id,
        CompletedSurvey.completed_at >= _start_of_today_utc(),
    ).count()


@survey_bp.route("/surveys", methods=["GET"])
@jwt_required()
def list_surveys():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    benefits = user.tier_benefits

    completed_ids = {
        cs.survey_id for cs in CompletedSurvey.query.filter_by(user_id=user_id).all()
    }
    surveys = Survey.query.filter_by(status="active").order_by(Survey.created_at.desc()).all()

    return jsonify({
        "surveys": [s.to_dict(completed_by_user=s.id in completed_ids) for s in surveys],
        "tier": user.tier,
        "tier_label": benefits["label"],
        "reward_min": benefits["reward_min"],
        "reward_max": benefits["reward_max"],
        "daily_survey_limit": benefits["daily_survey_limit"],
        "surveys_taken_today": _surveys_completed_today(user_id),
    }), 200


@survey_bp.route("/survey/<int:survey_id>", methods=["GET"])
@jwt_required()
def get_survey(survey_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"error": "Survey not found"}), 404

    already_completed = CompletedSurvey.query.filter_by(
        user_id=user_id, survey_id=survey_id
    ).first() is not None

    benefits = user.tier_benefits
    daily_limit = benefits["daily_survey_limit"]
    taken_today = _surveys_completed_today(user_id)

    survey_data = survey.to_dict(include_questions=True, completed_by_user=already_completed)
    survey_data["reward_min"] = benefits["reward_min"]
    survey_data["reward_max"] = benefits["reward_max"]
    survey_data["daily_survey_limit"] = daily_limit
    survey_data["surveys_taken_today"] = taken_today
    survey_data["limit_reached"] = daily_limit is not None and taken_today >= daily_limit

    return jsonify({"survey": survey_data}), 200


@survey_bp.route("/survey/<int:survey_id>/submit", methods=["POST"])
@jwt_required()
def submit_survey(survey_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"error": "Survey not found"}), 404

    if survey.status != "active":
        return jsonify({"error": "This survey is no longer active"}), 400

    already_completed = CompletedSurvey.query.filter_by(
        user_id=user_id, survey_id=survey_id
    ).first()
    if already_completed:
        return jsonify({"error": "You have already completed this survey"}), 409

    benefits = user.tier_benefits
    daily_limit = benefits["daily_survey_limit"]
    if daily_limit is not None and _surveys_completed_today(user_id) >= daily_limit:
        return jsonify({
            "error": f"You've reached your daily limit of {daily_limit} survey(s) on the "
                     f"{benefits['label']} plan. Upgrade your account to take more surveys today.",
            "limit_reached": True,
        }), 403

    data = request.get_json(silent=True) or {}
    answers = data.get("answers", {})  # { question_id: answer_value }

    question_ids = [q.id for q in survey.questions]
    for qid in question_ids:
        answer = answers.get(str(qid), answers.get(qid))
        if answer is None or (isinstance(answer, str) and not answer.strip()):
            return jsonify({"error": "All questions must be answered before submitting"}), 400

    reward = random.randint(int(benefits["reward_min"]), int(benefits["reward_max"]))

    completion = CompletedSurvey(user_id=user_id, survey_id=survey_id)
    db.session.add(completion)

    user.wallet_balance += reward
    user.total_earned += reward

    db.session.commit()

    return jsonify({
        "message": "Survey completed successfully",
        "reward": reward,
        "wallet_balance": round(user.wallet_balance, 2),
        "surveys_taken_today": _surveys_completed_today(user_id),
        "daily_survey_limit": daily_limit,
    }), 200
