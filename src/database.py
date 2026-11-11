import sqlite3
from typing import Any, Dict, List, Optional

class DatabaseRepository:
 MAX_NAME_LEN = 256
 MAX_MESSAGE_LEN = 8096

 def __init__(self, db_path: str = ':memory:'):
 self.db_path = db_path
 self.connection = sqlite3.connect(self.db_path)
 self._create_table()

 def _create_table(self) -> None:
 with self.connection:
 self.connection.execute(
 'CREATE TABLE IF NOT EXISTS comments ('
 'id INTEGER PRIMARY KEY, '
 'name TEXT NOT NULL, '
 'message TEXT NOT NULL)'
 )

 @classmethod
 def _validate_id(cls, comment_id: Any) -> None:
 if not isinstance(comment_id, int) or isinstance(comment_id, bool) or comment_id <= 0:
 raise ValueError('ID должен быть положительным целым числом.')

 @classmethod
 def _validate_name(cls, username: Any) -> None:
 if not isinstance(username, str) or not username.strip():
 raise ValueError('Имя пользователя должно быть непустой строкой.')
 if len(username) > cls.MAX_NAME_LEN:
 raise ValueError('Превышена максимальная длина имени (256).')

 @classmethod
 def _validate_message(cls, message: Any) -> None:
 if not isinstance(message, str) or not message.strip():
 raise ValueError('Сообщение должно быть непустой строкой.')
 if len(message) > cls.MAX_MESSAGE_LEN:
 raise ValueError('Превышена максимальная длина сообщения (8096).')

 def add(self, comment_id: int, username: str, message: str) -> bool:
 self._validate_id(comment_id)
 self._validate_name(username)
 self._validate_message(message)
 try:
 with self.connection:
 self.connection.execute(
 'INSERT INTO comments (id, name, message) VALUES (?, ?, ?)',
 (comment_id, username, message),
 )
 return True
 except sqlite3.IntegrityError as exc:
 raise ValueError(f'Запись с ID {comment_id} уже существует.') from exc

 def get_by_id(self, comment_id: int) -> Optional[Dict[str, Any]]:
 self._validate_id(comment_id)
 cursor = self.connection.cursor()
 cursor.execute('SELECT id, name, message FROM comments WHERE id = ?', (comment_id,))
 row = cursor.fetchone()
 if row is None:
 return None
 return {'id': row[0], 'name': row[1], 'message': row[2]}

 def get_by_name(self, username: str) -> List[Dict[str, Any]]:
 self._validate_name(username)
 cursor = self.connection.cursor()
 cursor.execute('SELECT id, name, message FROM comments WHERE name = ? ORDER BY id ASC', (username,))
 rows = cursor.fetchall()
 return [{'id': r[0], 'name': r[1], 'message': r[2]} for r in rows]

 def update(self, comment_id: int, new_message: str) -> bool:
 self._validate_id(comment_id)
 self._validate_message(new_message)
 with self.connection:
 cursor = self.connection.execute(
 'UPDATE comments SET message = ? WHERE id = ?',
 (new_message, comment_id),
 )
 if cursor.rowcount == 0:
 raise KeyError(f'Запись с ID {comment_id} не найдена.')
 return True

 def delete(self, comment_id: int) -> bool:
 self._validate_id(comment_id)
 with self.connection:
 cursor = self.connection.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
 if cursor.rowcount == 0:
 raise KeyError(f'Запись с ID {comment_id} не найдена.')
 return True

 def close(self) -> None:
 if self.connection:
 self.connection.close()