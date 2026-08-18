import unittest
from unittest.mock import patch
from backend.modules.module4.module4_store import create_session, get_session, save_session, list_sessions

class Module4StoreTests(unittest.TestCase):
    def test_store_requires_user_scope(self):
        with patch('module4_store.ensure_schema'), patch('module4_store.db_connect') as connect:
            conn=connect.return_value.__enter__.return_value
            cur=conn.cursor.return_value.__enter__.return_value
            cur.fetchone.return_value=None
            self.assertIsNone(get_session('user-a','missing'))
            cur.execute.assert_called_once()
            self.assertIn('user_id=%s',cur.execute.call_args.args[0])

    def test_save_rejects_missing_owned_session(self):
        state={'id':'s1','question_index':1,'events':[],'status':'IN_PROGRESS'}
        with patch('module4_store.ensure_schema'), patch('module4_store.db_connect') as connect:
            conn=connect.return_value.__enter__.return_value
            cur=conn.cursor.return_value.__enter__.return_value
            cur.rowcount=0
            with self.assertRaises(LookupError): save_session('user-a',state)

    def test_list_is_bounded(self):
        with patch('module4_store.ensure_schema'), patch('module4_store.db_connect') as connect:
            conn=connect.return_value.__enter__.return_value
            cur=conn.cursor.return_value.__enter__.return_value
            cur.fetchall.return_value=[]
            self.assertEqual(list_sessions('user-a',999),[])
            params=cur.execute.call_args.args[-1]
            self.assertEqual(params[0],'user-a')
            self.assertEqual(params[1],100)

if __name__=='__main__': unittest.main()
