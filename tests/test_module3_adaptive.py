from backend.modules.module3.module3_adaptive import initial_state, select_next_question, update_skill_state, record_code_signal
from backend.modules.module3.module3_routes import QUESTIONS


def test_adaptive_state_is_bounded_and_persistent_shape():
    state = initial_state(3)
    assert state['ability'] == 50.0
    assert set(state['skill_scores']) == {'python', 'algorithms', 'system_design'}


def test_adaptive_policy_targets_weakest_skill():
    state = initial_state(3)
    state['skill_scores']['algorithms'] = 25
    assert select_next_question(QUESTIONS, state)['id'] == 'tech-02'


def test_answer_evidence_updates_skill_without_exceeding_bounds():
    state = initial_state(3)
    update_skill_state(state, QUESTIONS[1], {'score': 100})
    assert state['skill_evidence']['algorithms'] == 1
    assert 0 <= state['skill_scores']['algorithms'] <= 100
    assert 0 <= state['ability'] <= 100


def test_code_signal_is_recorded_as_evidence():
    state = initial_state(3)
    record_code_signal(state, {'score': 90})
    assert state['skill_evidence']['python'] == 1
    assert 0 <= state['skill_scores']['python'] <= 100
