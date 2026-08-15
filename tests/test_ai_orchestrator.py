import json
import os
import unittest
from unittest.mock import patch

from ai.orchestrator import AIOrchestrator, AIProviderError
from ai.providers import AIResponse, DeepSeekProvider


class FakeProvider:
    name = 'deepseek'
    def __init__(self, content):
        self.content = content
    def generate(self, *args, **kwargs):
        return AIResponse(self.content, 'deepseek', 'test-model', 'req-test', 3, {'total_tokens': 5}, {})
    def stream(self, *args, **kwargs):
        yield 'hello'
        yield ' world'
    def health(self):
        return {'provider': 'deepseek', 'configured': True}


class AIOrchestratorTests(unittest.TestCase):
    def test_structured_output_validation(self):
        orch = AIOrchestrator()
        orch.providers = {'deepseek': FakeProvider(json.dumps({'ok': 'yes'}))}
        schema = {'type': 'object', 'required': ['ok'], 'properties': {'ok': {'type': 'string'}}}
        result = orch.generate_structured(user_id='u1', feature='test', task='return ok', context={}, schema=schema, retries=0)
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['ok'], 'yes')

    def test_malformed_output_fails_honestly(self):
        orch = AIOrchestrator()
        orch.providers = {'deepseek': FakeProvider('{bad json')}
        schema = {'type': 'object', 'required': ['ok'], 'properties': {'ok': {'type': 'string'}}}
        with self.assertRaises(AIProviderError):
            orch.generate_structured(user_id='u1', feature='test', task='return ok', context={}, schema=schema, retries=0)

    def test_stream_aggregates_in_order(self):
        orch = AIOrchestrator()
        orch.providers = {'deepseek': FakeProvider('ignored')}
        self.assertEqual(''.join(orch.stream(feature='test', task='hello', context={})), 'hello world')

    def test_no_browser_key_name(self):
        provider = DeepSeekProvider()
        self.assertFalse(hasattr(provider, 'NEXT_PUBLIC_DEEPSEEK_API_KEY'))


if __name__ == '__main__':
    unittest.main()
