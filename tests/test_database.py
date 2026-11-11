import unittest
from src.database import DatabaseRepository

class TestDatabaseRepository(unittest.TestCase):
 def setUp(self):
 self.repo = DatabaseRepository(db_path=':memory:')

 def tearDown(self):
 self.repo.close()

 def test_add_success(self):
 self.assertTrue(self.repo.add(1, 'user_one', '<p>Привет!</p>'))
 self.assertEqual(self.repo.get_by_id(1)['name'], 'user_one')

 def test_add_duplicate_id_raises_error(self):
 self.repo.add(1, 'user_one', 'Первое сообщение')
 with self.assertRaises(ValueError):
 self.repo.add(1, 'user_two', 'Дубликат ID')

 def test_add_exceeding_max_length_raises_error(self):
 with self.assertRaises(ValueError):
 self.repo.add(2, 'a' * 257, 'Текст')

 def test_get_by_id_existing_record(self):
 self.repo.add(10, 'alex', '<b>Текст</b>')
 self.assertEqual(self.repo.get_by_id(10), {'id': 10, 'name': 'alex', 'message': '<b>Текст</b>'})

 def test_get_by_id_non_existent_returns_none(self):
 self.assertIsNone(self.repo.get_by_id(999))

 def test_get_by_name_multiple_records(self):
 self.repo.add(1, 'ivan', 'Пост 1')
 self.repo.add(2, 'ivan', 'Пост 2')
 self.assertEqual(len(self.repo.get_by_name('ivan')), 2)

 def test_get_by_name_no_matches_returns_empty_list(self):
 self.assertEqual(self.repo.get_by_name('unknown'), [])

 def test_update_existing_record_success(self):
 self.repo.add(5, 'editor', 'Старый')
 self.assertTrue(self.repo.update(5, '<i>Новый</i>'))
 self.assertEqual(self.repo.get_by_id(5)['message'], '<i>Новый</i>')

 def test_update_non_existent_id_raises_error(self):
 with self.assertRaises(KeyError):
 self.repo.update(404, 'Нет записи')

 def test_delete_existing_record_success(self):
 self.repo.add(7, 'temp_user', 'Удалить')
 self.assertTrue(self.repo.delete(7))
 self.assertIsNone(self.repo.get_by_id(7))

 def test_delete_non_existent_id_raises_error(self):
 with self.assertRaises(KeyError):
 self.repo.delete(888)

if __name__ == '__main__':
 unittest.main()