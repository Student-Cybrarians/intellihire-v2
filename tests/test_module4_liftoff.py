import os
import unittest
from module4_liftoff import start, question, answer, finish, score_transcript, model_feedback

class Module4LiftoffBackendTests(unittest.TestCase):
    def setUp(self):
        self._env = {k: os.environ.get(k) for k in ('NVIDIA_API_KEY','OPENAI_API_KEY')}
        os.environ.pop('NVIDIA_API_KEY', None)
        os.environ.pop('OPENAI_API_KEY', None)

    def tearDown(self):
        for k, v in self._env.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v

    def test_deterministic_star_and_filler_analysis(self):
        result = score_transcript(
            'In the project situation, I was responsible for the migration goal. '
            'I led the team, implemented the rollout, resolved blockers, and improved delivery by 20 percent.',
            'Tell me about a difficult project or responsibility you owned.'
        )
        self.assertEqual(result['star']['situation'], 1)
        self.assertEqual(result['star']['task'], 1)
        self.assertEqual(result['star']['action'], 1)
        self.assertEqual(result['star']['result'], 1)
        self.assertGreaterEqual(result['star_score'], 75)
        self.assertEqual(result['filler_count'], 0)

    def test_interview_lifecycle_without_external_ai(self):
        state = start('Software Engineer')
        self.assertEqual(state['status'], 'IN_PROGRESS')
        self.assertIsNotNone(question(state))
        event = answer(state, 'I led the team and resolved the issue, which improved delivery and reduced delays.')
        self.assertIn('metrics', event)
        self.assertIsNotNone(question(state))
        report = finish(state)
        self.assertEqual(report['status'], 'COMPLETED')
        self.assertIn('score', report)

    def test_provider_fallback_is_safe_without_keys(self):
        self.assertIsNone(model_feedback('Tell me about a challenge.', 'I solved a challenge.'))

if __name__ == '__main__':
    unittest.main()
