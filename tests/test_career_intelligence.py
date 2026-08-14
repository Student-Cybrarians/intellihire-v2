from career_intelligence import build_career_twin, build_roadmap, extract_skills


def test_skill_extraction_normalizes_aliases():
    skills = extract_skills('Python, React.js, NodeJS, PostgreSQL, AWS, machine learning')
    assert 'python' in skills
    assert 'react' in skills
    assert 'node.js' in skills
    assert 'postgresql' in skills
    assert 'aws' in skills
    assert 'machine learning' in skills


def test_career_twin_separates_evidence_and_gaps():
    resume = 'Built Python REST APIs with Flask and PostgreSQL. Used Docker in deployment.'
    jd = 'Need Python, Flask, PostgreSQL, Docker, Kubernetes and AWS.'
    twin = build_career_twin(resume, jd, 'Backend Engineer')
    assert set(twin['matched_skills']) >= {'python', 'flask', 'postgresql', 'docker'}
    assert set(twin['skill_gaps']) == {'aws', 'kubernetes'}
    assert twin['integrity']['fabrication'] is False
    assert all(x['state'] != 'evidenced' or x['evidence'] for x in twin['skill_graph'])


def test_roadmap_is_bounded_and_actionable():
    twin = {'skill_gaps': ['aws', 'kubernetes', 'terraform']}
    roadmap = build_roadmap(twin, weeks=2)
    assert len(roadmap) == 2
    assert roadmap[0]['week'] == 1
    assert roadmap[0]['evidence']
