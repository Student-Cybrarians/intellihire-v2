from backend.intelligence.roadmap_engine import generate_roadmap


def test_roadmap_is_bounded_and_evidence_linked():
    twin={
        'role':'Backend Engineer',
        'skill_gaps':['python','docker'],
        'skill_graph':[{'skill':'python','state':'gap','evidence':''},{'skill':'docker','state':'gap','evidence':''}],
    }
    research={'sources':[{'url':'https://docs.python.org/3/','title':'Python docs'}]}
    plan=generate_roadmap(twin,research,weeks=30)
    assert len(plan['milestones']) == 2
    assert plan['source_urls'] == ['https://docs.python.org/3/']
    assert plan['integrity']['fabricated_candidate_experience'] is False
    assert all('deliverables' in item['project'] for item in plan['milestones'])


def test_roadmap_does_not_claim_gap_as_evidence():
    twin={'role':'ML Engineer','skill_gaps':['pytorch'],'skill_graph':[{'skill':'pytorch','state':'gap','evidence':''}]}
    plan=generate_roadmap(twin,{},1)
    project=plan['milestones'][0]['project']
    assert 'pytorch' in project['objective'].lower()
    assert project['evidence_required']
    assert project['status'] == 'planned'
