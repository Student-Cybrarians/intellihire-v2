import json
import pytest
import backend.research.research_retrieval


def test_retrieve_requires_configured_provider(monkeypatch):
    monkeypatch.delenv('TAVILY_API_KEY', raising=False)
    assert research_retrieval.retrieve('learn python')[1] == 'not_configured'


def test_retrieve_normalizes_results(monkeypatch):
    monkeypatch.setenv('TAVILY_API_KEY','test-key')
    class Response:
        def raise_for_status(self): pass
        def json(self): return {'results':[{'title':'Python Docs','url':'https://docs.python.org/3/','content':'Official Python documentation'}]}
    monkeypatch.setattr(research_retrieval.requests,'post',lambda *a,**k: Response())
    records,status=research_retrieval.retrieve('python')
    assert status == 'live'
    assert records[0]['url'].startswith('https://')
    assert records[0]['publisher'] == 'docs.python.org'


def test_synthesis_rejects_untrusted_citations(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test-key')
    monkeypatch.setattr(research_retrieval,'_chat',lambda *a,**k: json.dumps({'answer':'grounded','key_findings':[],'implications_for_candidate':[],'learning_actions':[],'citations':['https://evil.example/not-supplied']}))
    result=research_retrieval.synthesize({'question':'q','sources':[{'title':'Trusted','url':'https://trusted.example/a','snippet':'evidence'}]})
    assert result['is_ai'] is True
    assert result['citations'] == []


def test_synthesis_falls_back_without_ai(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    monkeypatch.delenv('NVIDIA_API_KEY',raising=False)
    result=research_retrieval.synthesize({'question':'q','sources':[{'title':'Trusted','url':'https://trusted.example/a','snippet':'evidence'}],'claims':[{'evidence':'evidence','source_url':'https://trusted.example/a'}]})
    assert result['provider'] == 'deterministic-fallback'
    assert result['is_ai'] is False
    assert result['citations'] == ['https://trusted.example/a']


def test_run_research_uses_supplied_sources_without_network(monkeypatch):
    monkeypatch.setattr(research_retrieval,'retrieve',lambda *a,**k: (_ for _ in ()).throw(AssertionError('network should not be called')))
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    monkeypatch.delenv('NVIDIA_API_KEY',raising=False)
    result=research_retrieval.run_research({},'q',[{'title':'Source','url':'https://example.com','snippet':'evidence'}])
    assert result['retrieval_status'] == 'supplied'
    assert result['sources'][0]['url'] == 'https://example.com'
