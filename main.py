import os
from src.database import DatabaseRepository
from src.parser import ForumParser

def main():
 db_file = 'forum.db'
 if os.path.exists(db_file):
 os.remove(db_file)

 target_url = 'https://quotes.toscrape.com/'
 print(f'=== 1. Отправка GET-запроса на реальный сайт: {target_url} ===')
 parser = ForumParser()
 parsed_posts = parser.parse_page(target_url)
 print(f'-> Успешно скачано и распарсено постов: {len(parsed_posts)}')

 print(f'=== 2. Сохранение распарсенных данных в файл БД: {db_file} ===')
 repo = DatabaseRepository(db_path=db_file)
 saved = parser.save_to_db(parsed_posts, repo)
 print(f'-> Успешно добавлено записей в таблицу comments: {saved}')

 print('=== 3. Проверка чтения из SQLite БД ===')
 sample = repo.get_by_id(1)
 print(f'Запись ID=1: Автор: [{sample["name"]}] | Текст: {sample["message"][:60]}...')

 repo.close()
 print('=== Работа завершена: данные сохранены в forum.db ===')

if __name__ == '__main__':
 main()