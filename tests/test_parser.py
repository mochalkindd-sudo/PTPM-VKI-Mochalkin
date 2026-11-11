import os
import unittest
from unittest.mock import MagicMock, patch
from src.database import DatabaseRepository
from src.parser import ForumParser

class TestForumParser(unittest.TestCase):
 def setUp(self):
 self.parser = ForumParser()
 self.db = DatabaseRepository(db_path=':memory:')
 fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'forum_sample.html')
 with open(fixture_path, 'r', encoding='utf-8') as f:
 self.sample_html = f.read()

 def tearDown(self):
 self.db.close()

 @patch('src.parser.requests.get')
 def test_parse_page_extracts_all_comments_from_fixture(self, mock_get):
 mock_response = MagicMock(status_code=200, text=self.sample_html)
 mock_get.return_value = mock_response
 parsed = self.parser.parse_page('https://example-forum.local/thread/1')
 mock_get.assert_called_once()
 self.assertIn('User-Agent', mock_get.call_args.kwargs.get('headers', {}))
 self.assertEqual(len(parsed), 3)
 self.assertEqual(parsed[0]['id'], 101)
 self.assertEqual(parsed[0]['name'], 'dev_master')
 self.assertIn('<b>unittest</b>', parsed[0]['message'])

 @patch('src.parser.requests.get')
 def test_parse_page_and_save_to_db(self, mock_get):
 mock_get.return_value = MagicMock(status_code=200, text=self.sample_html)
 parsed_data = self.parser.parse_page('https://example-forum.local/thread/1')
 saved_count = self.parser.save_to_db(parsed_data, self.db)
 self.assertEqual(saved_count, 3)
 self.assertEqual(len(self.db.get_by_name('dev_master')), 2)
 self.assertEqual(self.db.get_by_id(102)['name'], 'python_fan')

 def test_parse_empty_html_returns_empty_list(self):
 self.assertEqual(self.parser.parse_html('<html><body></body></html>'), [])

if __name__ == '__main__':
 unittest.main()