import pytest

from module2_engine import QUESTION_BANK, evaluate_answer, score_assessment
from module2_store import create_assessment, get_assessment


def test_create_assessment_rejects_out_of_range_without_db(monkeypatch):
    monkeypatch.setattr('module2_store.init_module2_store', lambda: (_ for _ in ()).throw(AssertionError('db should not be reached')))
    with pytest.raises(ValueError, match='invalid_target_questions'):
        create_assessment('user-id', target_questions=0)
    with pytest.raises(ValueError, match='invalid_target_questions'):
        create_assessment('user-id', target_questions=101)


def test_get_assessment_rejects_invalid_identifier_without_db(monkeypatch):
    monkeypatch.setattr('module2_store.db_connect', lambda: (_ for _ in ()).throw(AssertionError('db should not be reached')))
    assert get_assessment('user-id', 'not-a-uuid') is None


def test_adaptive_answer_never_exposes_answer_in_public_event():
    question = QUESTION_BANK[0]
    event = evaluate_answer(0.0, question, question.answer)
    assert event['correct'] is True
    assert event['question']['answer'] == question.answer
    public_question = {k: v for k, v in event['question'].items() if k != 'answer'}
    assert 'answer' not in public_question


def test_completed_assessment_score_is_bounded():
    events = []
    theta = 0.0
    for question in QUESTION_BANK:
        event = evaluate_answer(theta, question, question.answer)
        theta = event['ability_after']
        events.append(event)
    result = score_assessment(events)
    assert 0 <= result['score'] <= 100
    assert result['questions'] == len(QUESTION_BANK)
