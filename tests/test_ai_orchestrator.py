import json
import os
import unittest
from unittest.mock import patch
from ai.orchestrator import AIOrchestrator, AIProviderError
from ai.providers import AIResponse, DeepSeekProvider

class FakeProvider:
    name='fake'
    def __init__(self, content): self.content=content
    def generate(self,*args,**kwargs): return AIResponse(self.content,'fake','test-model','req-test',3,{'total_tokens':5},{})
    def stream(self,*args,**kwargs): yield 'hello'; yield ' world'
    def health(self): return {'provider':'fake','configured':True}

class AIOrchestratorTests(unittest.TestCase):
    def test_structured_output_validation(self):
        orch=AIOrchestrator(); orch.providers={'fake':FakeProvider(json.dumps({'ok':'yes'}))}
        with patch.dict(os.environ,{'INTELLIHIRE_AI_PROVIDER':'fake'},clear=False):
            result=orch.generate_structured(user_id='u1',feature='test',task='return ok',context={},schema={'type':'object','required':['ok'],'properties':{'ok':{'type':'string'}}},retries=0)
        self.assertTrue(result['success']); self.assertEqual(result['data']['ok'],'yes')
    def test_malformed_output_fails_honestly(self):
        orch=AIOrchestrator(); orch.providers={'fake':FakeProvider('{bad json')}
        with patch.dict(os.environ,{'INTELLIHIRE_AI_PROVIDER':'fake'},clear=False):
            with self.assertRaises(AIProviderError): orch.generate_structured(user_id='u1',feature='test',task='return ok',context={},schema={'type':'object','required':['ok'],'properties':{'ok':{'type':'string'}}},retries=0)
    def test_stream_aggregates_in_order(self):
        orch=AIOrchestrator(); orch.providers={'fake':FakeProvider('ignored')}
        with patch.dict(os.environ,{'INTELLIHIRE_AI_PROVIDER':'fake'},clear=False): self.assertEqual(''.join(orch.stream(feature='test',task='hello',context={})), 'hello world')
    def test_no_browser_key_name(self): self.assertFalse(hasattr(DeepSeekProvider(),'NEXT_PUBLIC_DEEPSEEK_API_KEY'))

if __name__=='__main__': unittest.main()

# Final verification trigger after deterministic research fallback fix.
