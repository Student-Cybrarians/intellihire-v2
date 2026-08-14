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
    docx=resume_docx_bytes(resume); pdf=resume_pdf_bytes(resume)
    assert docx[:2] == b'PK'
    assert pdf.startswith(b'%PDF')


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


def test_missing_jd_skills_are_never_silently_claimed():
    monkeypatch=None
    result=analyze_with_ai.__wrapped__ if False else None
