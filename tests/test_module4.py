import unittest
from backend.modules.module4.module4_liftoff import start, question, answer, finish, score_transcript


class Module4EngineTests(unittest.TestCase):
    def test_star_analysis(self):
        result = score_transcript(
            'In a project situation I was responsible for a goal and built a solution that improved delivery and achieved the result.',
            'Tell me about a difficult project or responsibility you owned.'
        )
        self.assertIn('star_score', result)
        self.assertGreaterEqual(result['clarity'], 55)

    def test_interview_lifecycle(self):
        state = start_interview_compat()
        self.assertEqual(state['status'], 'IN_PROGRESS')
        question_data = question(state)
        self.assertIsNotNone(question_data)
        event = answer(state, 'I led the team, resolved the issue and improved the result.')
        self.assertIn('metrics', event)
        result = finish(state)
        self.assertEqual(state['status'], 'COMPLETED')
        self.assertIn('score', result)


def start_interview_compat():
    return start()


if __name__ == '__main__':
    unittest.main()
