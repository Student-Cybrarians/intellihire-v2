import unittest
from module4_hr import start_interview, next_question, submit_answer, finish_interview, analyze_answer

class Module4EngineTests(unittest.TestCase):
    def test_star_analysis(self):
        result = analyze_answer('In a project situation I was responsible for a goal and built a solution that improved delivery and achieved the result.')
        self.assertIn('star_score', result)
        self.assertGreaterEqual(result['clarity'], 55)

    def test_interview_lifecycle(self):
        state = start_interview()
        self.assertEqual(state['status'], 'CREATED')
        question = next_question(state)
        self.assertIsNotNone(question)
        event = submit_answer(state, 'I led the team, resolved the issue and improved the result.')
        self.assertIn('metrics', event)
        result = finish_interview(state)
        self.assertEqual(state['status'], 'COMPLETED')
        self.assertIn('score', result)

if __name__ == '__main__':
    unittest.main()
