import json

import module1_ai
from ml_engine import analyze_resume, bm25_score, career_gap_analysis, build_career_context, match_resume_to_job, normalize_skill, research_plan
from module1_ai import _deterministic_metrics, _extract_json, analyze_with_ai, resume_csv_bytes, resume_docx_bytes, resume_pdf_bytes


def test_json_parser_handles_fenced_json():
    assert _extract_json('```json\n{"ats_score": 91}\n```')['ats_score'] == 91


def test_deterministic_baseline_matches_jd_skills():
    m = _deterministic_metrics('Python React Docker Git', 'Python React AWS Docker Git')
    assert 'python' in m['matched_skills']
    assert 'aws' in m['missing_skills']
    assert 0 <= m['ats_baseline'] <= 100


def test_csv_export_is_real_bytes():
    data = resume_csv_bytes({'name': 'Candidate', 'skills': ['Python', 'SQL']})
    assert data.startswith(b'\xef\xbb\xbf')
    assert b'Candidate' in data
    assert b'Python' in data


def test_docx_and_pdf_exports_are_real_files():
    resume={'name':'Candidate','headline':'Engineer','summary':'Python developer','skills':['Python'],'experience':['Built APIs'],'education':['B.Tech'],'projects':['ATS project'],'certifications':['AWS']}
    assert resume_docx_bytes(resume)[:2] == b'PK'
    assert resume_pdf_bytes(resume).startswith(b'%PDF')


def test_ai_fallback_is_explicit(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('NVIDIA_API_KEY', raising=False)
    result=analyze_with_ai('Python developer with Git','Python and Git required','Acme','Software Engineer')
    assert result['is_ai'] is False
    assert result['provider'] == 'deterministic-fallback'
    assert 'tailored_resume' in result
    assert result['company'] == 'Acme'
    assert result['role'] == 'Software Engineer'


def test_required_output_contract(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('NVIDIA_API_KEY', raising=False)
    result=analyze_with_ai('Python developer','Python Docker AWS required','Acme','Engineer')
    required={'ats_score','overall_match','keyword_match','semantic_match','skills_match','matched_skills','missing_skills','recommendations','learning_plan','recommended_certifications','tailored_resume','shortlist'}
    assert required.issubset(result)
    skills=[x.lower() for x in result['tailored_resume']['skills']]
    assert '[verify] docker' in skills
    assert '[verify] aws' in skills


def _ai_payload(score=88):
    return {
        'ats_score': score, 'overall_match': 86, 'keyword_match': 90,
        'semantic_match': 82, 'skills_match': 85,
        'matched_skills': ['python'], 'missing_skills': ['docker'],
        'strengths': ['python'], 'risks': ['docker'],
        'recommendations': ['Learn Docker'],
        'recruiter_feedback': 'Good fit with one gap.',
        'learning_plan': ['Build a Docker project'],
        'recommended_certifications': [],
        'tailored_resume': {
            'name': 'Candidate', 'headline': 'Engineer', 'summary': 'Python engineer',
            'skills': ['Python'], 'experience': [], 'education': [], 'projects': [],
            'certifications': [], 'keywords': ['python', 'docker']
        }
    }


def test_openai_real_provider_contract(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test-openai-key')
    monkeypatch.delenv('NVIDIA_API_KEY', raising=False)
    calls=[]

    class Response:
        def raise_for_status(self): pass
        def json(self): return {'choices':[{'message':{'content':json.dumps(_ai_payload())}}]}

    def fake_post(endpoint, **kwargs):
        calls.append((endpoint,kwargs))
        return Response()

    monkeypatch.setattr(module1_ai.requests, 'post', fake_post)
    result=analyze_with_ai('Python developer','Python and Docker required','Acme','Engineer')
    assert result['is_ai'] is True
    assert result['provider'] == 'openai'
    assert result['ats_score'] == 88
    assert calls[0][0] == 'https://api.openai.com/v1/chat/completions'
    assert calls[0][1]['json']['messages'][0]['role'] == 'system'
    assert calls[0][1]['timeout'] <= 10


def test_nvidia_fallback_after_openai_failure(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','bad-openai-key')
    monkeypatch.setenv('NVIDIA_API_KEY','test-nvidia-key')
    endpoints=[]

    class Response:
        def __init__(self, fail=False): self.fail=fail
        def raise_for_status(self):
            if self.fail: raise RuntimeError('provider failure')
        def json(self): return {'choices':[{'message':{'content':json.dumps(_ai_payload(81))}}]}

    def fake_post(endpoint, **kwargs):
        endpoints.append(endpoint)
        return Response(fail=endpoint.startswith('https://api.openai.com'))

    monkeypatch.setattr(module1_ai.requests, 'post', fake_post)
    result=analyze_with_ai('Python developer','Python required','Acme','Engineer')
    assert result['is_ai'] is True
    assert result['provider'] == 'nvidia'
    assert endpoints == ['https://api.openai.com/v1/chat/completions','https://integrate.api.nvidia.com/v1/chat/completions']


def test_provider_timeout_returns_without_hanging(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','slow-openai-key')
    monkeypatch.delenv('NVIDIA_API_KEY', raising=False)
    monkeypatch.setenv('MODULE1_AI_PROVIDER_TIMEOUT_SECONDS','2')
    monkeypatch.setenv('MODULE1_AI_TOTAL_TIMEOUT_SECONDS','2')

    def fake_post(endpoint, **kwargs):
        assert kwargs['timeout'] <= 2
        raise module1_ai.requests.Timeout('simulated provider timeout')

    monkeypatch.setattr(module1_ai.requests, 'post', fake_post)
    result=analyze_with_ai('Python developer','Python required','Acme','Engineer')
    assert result['is_ai'] is False
    assert result['provider'] == 'deterministic-fallback'
    assert 'timeout' in (result['ai_error'] or '').lower()


def test_skill_alias_normalization():
    assert normalize_skill('JS') == 'javascript'
    assert normalize_skill('ReactJS') == 'react'
    assert normalize_skill('Postgres') == 'postgresql'


def test_resume_ml_analysis_is_evidence_based():
    result = analyze_resume('Python developer with React and Docker. B.Tech Computer Science. experience @example.com')
    assert 'python' in result['skills']
    assert result['sections']['education'] is True
    assert result['score'] <= 100


def test_resume_job_matching_has_real_ml_method_label():
    result = match_resume_to_job('Python React Docker developer', 'Python React Docker AWS required')
    assert result['isSimulated'] is False
    assert result['method'] == 'skill+TFIDF+BM25'
    assert 'aws' in result['missingSkills']
    assert 0 <= result['atsScore'] <= 100


def test_bm25_is_non_negative():
    assert bm25_score('python docker', 'python python docker aws') >= 0


def test_career_context_and_gap_engine():
    profile = {'name': 'Candidate', 'target_role': 'Backend Engineer', 'skills': ['Python', 'SQL']}
    context = build_career_context(profile, [{'module': 'module2', 'score': 72}], 'Backend Engineer')
    gap = career_gap_analysis(profile, 'Backend Engineer')
    plan = research_plan(profile, 'Backend Engineer')
    assert context['goal'] == 'Backend Engineer'
    assert 'docker' in gap['missingSkills']
    assert plan['actions']
    assert plan['sources'] == []
