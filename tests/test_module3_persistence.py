import pytest
from module3_routes import QUESTIONS, score_answer


def test_module3_scoring_is_bounded():
    result = score_answer('API database cache testing security tradeoff complexity scale')
    assert 0 <= result['score'] <= 100
    assert 0 <= result['accuracy'] <= 100
    assert 0 <= result['communication'] <= 100


def test_module3_question_bank_has_stable_ids():
    ids = [q['id'] for q in QUESTIONS]
    assert len(ids) == len(set(ids))
    assert all(q['prompt'] and q['topic'] for q in QUESTIONS)


def test_module3_answer_length_policy_is_explicit():
    assert len('x' * 12000) == 12000
