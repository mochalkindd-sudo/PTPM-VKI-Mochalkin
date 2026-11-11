import re
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup, FeatureNotFound
from src.database import DatabaseRepository

class ForumParser:
 DEFAULT_HEADERS = {
 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
 }

 def __init__(self, headers: Optional[Dict[str, str]] = None):
 self.headers = headers or self.DEFAULT_HEADERS.copy()

 @staticmethod
 def _make_soup(html_content: str) -> BeautifulSoup:
 try:
 return BeautifulSoup(html_content, 'lxml')
 except FeatureNotFound:
 return BeautifulSoup(html_content, 'html.parser')

 def parse_page(self, url: str) -> List[Dict[str, Any]]:
 response = requests.get(url, headers=self.headers, timeout=10)
 response.raise_for_status()
 return self.parse_html(response.text)

 def parse_html(self, html_content: str) -> List[Dict[str, Any]]:
 soup = self._make_soup(html_content)
 results: List[Dict[str, Any]] = []
 for elem in soup.select('.comment, .post, article[data-comment-id]'):
 raw_id = elem.get('data-id') or elem.get('data-comment-id') or elem.get('id', '')
 match = re.search(r'\d+', str(raw_id))
 if not match:
 continue
 comment_id = int(match.group(0))
 author_elem = elem.select_one('.author, .username, .user-name')
 msg_elem = elem.select_one('.message, .post-content, .comment-body')
 if not author_elem or not msg_elem:
 continue
 username = author_elem.get_text(strip=True)
 message_html = msg_elem.decode_contents().strip()
 if username and message_html:
 results.append({'id': comment_id, 'name': username, 'message': message_html})
 return results

 def save_to_db(self, parsed_data: List[Dict[str, Any]], repository: DatabaseRepository) -> int:
 saved_count = 0
 for item in parsed_data:
 repository.add(item['id'], item['name'], item['message'])
 saved_count += 1
 return saved_count