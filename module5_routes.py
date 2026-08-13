from flask import Blueprint, jsonify, request

from module5_engine import evaluate

module5 = Blueprint(
    "module5",
    __name__,
    url_prefix="/api/module5",
)


@module5.post("/evaluate")
def evaluate_route():
    data = request.get_json(silent=True) or {}
    return jsonify(evaluate(data.get("scores")))


@module5.get("/summary")
def summary():
    return jsonify(evaluate())
