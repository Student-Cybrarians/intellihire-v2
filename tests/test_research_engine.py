import pytest
from research_engine import build_research_brief


def test_research_brief_deduplicates_and_ranks_sources():
    twin={'skill_gaps':['kubernetes','aws']}
    sources=[
        {'title':'Kubernetes official docs','url':'https://kubernetes.io/docs/','snippet':'kubernetes deployment and workloads'},
        {'title':'AWS official docs','url':'https://aws.amazon.com/documentation/','snippet':'cloud infrastructure'},
        {'title':'Duplicate','url':'https://kubernetes.io/docs/','snippet':'duplicate'},
        {'title':'Invalid','url':'javascript:alert(1)','snippet':'bad'},
    ]
    result=build_research_brief(twin,'How should I learn kubernetes?',sources)
    assert len(result['sources'])==2
    assert result['sources'][0]['url']=='https://kubernetes.io/docs/'
    assert result['integrity']=={'fabricated_sources':False,'fabricated_claims':False}


def test_research_requires_question():
    with pytest.raises(ValueError,match='research_question_required'):
        build_research_brief({},'',[])
