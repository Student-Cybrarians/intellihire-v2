"""Deterministic adaptive policy for technical interviews.

The policy uses only persisted interview evidence. It never invents candidate
skills and never executes candidate code. AI evaluation remains optional and
is treated as evidence, not as a source of hidden state.
"""

SKILLS = ('python', 'algorithms', 'system_design')
QUESTION_SKILLS = {
    'tech-01': ('python',),
    'tech-02': ('algorithms',),
    'tech-03': ('system_design',),
}
DIFFICULTY = {'tech-01': 2, 'tech-02': 3, 'tech-03': 3}


def initial_state(total):
    return {
        'index': 0,
        'events': [],
        'total': int(total),
        'skill_scores': {skill: 50.0 for skill in SKILLS},
        'skill_evidence': {skill: 0 for skill in SKILLS},
        'ability': 50.0,
    }


def _bounded(value):
    return round(max(0.0, min(100.0, float(value))), 1)


def update_skill_state(state, question, evaluation):
    skills = tuple(QUESTION_SKILLS.get(question.get('id'), ()))
    if not skills:
        return state
    score = _bounded(evaluation.get('score', 0))
    for skill in skills:
        previous = float(state.setdefault('skill_scores', {}).get(skill, 50.0))
        evidence = int(state.setdefault('skill_evidence', {}).get(skill, 0))
        # More evidence gradually reduces volatility while preserving recent signal.
        weight = min(0.65, 0.35 + evidence * 0.1)
        state['skill_scores'][skill] = _bounded(previous * weight + score * (1.0 - weight))
        state['skill_evidence'][skill] = evidence + 1
    observed = [v for k, v in state['skill_scores'].items() if state['skill_evidence'].get(k, 0)]
    state['ability'] = _bounded(sum(observed) / len(observed)) if observed else 50.0
    return state


def select_next_question(questions, state):
    answered = {event.get('question_id') for event in state.get('events', [])}
    remaining = [q for q in questions if q.get('id') not in answered]
    if not remaining:
        return None
    scores = state.get('skill_scores', {})
    evidence = state.get('skill_evidence', {})
    # Prioritize the weakest evidenced skill; then prefer a question near current ability.
    weakest = min(SKILLS, key=lambda skill: (scores.get(skill, 50.0), evidence.get(skill, 0)))
    candidates = [q for q in remaining if weakest in QUESTION_SKILLS.get(q.get('id'), ())]
    if not candidates:
        candidates = remaining
    ability = float(state.get('ability', 50.0))
    return min(candidates, key=lambda q: (abs(DIFFICULTY.get(q.get('id'), 2) * 25 - ability), q.get('id', '')))


def record_code_signal(state, evaluation):
    """Feed static/AI code-evaluation evidence into the technical skill graph."""
    score = _bounded(evaluation.get('score', 0))
    state.setdefault('skill_scores', {}).setdefault('python', 50.0)
    state.setdefault('skill_evidence', {}).setdefault('python', 0)
    previous = state['skill_scores']['python']
    evidence = state['skill_evidence']['python']
    weight = min(0.7, 0.4 + evidence * 0.08)
    state['skill_scores']['python'] = _bounded(previous * weight + score * (1.0 - weight))
    state['skill_evidence']['python'] = evidence + 1
    observed = [v for k, v in state['skill_scores'].items() if state['skill_evidence'].get(k, 0)]
    state['ability'] = _bounded(sum(observed) / len(observed)) if observed else 50.0
    return state
