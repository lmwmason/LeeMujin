from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse


def get_search_results(query):
    base_url = "https://www.youtube.com/results"
    params = {'search_query': query}
    headers = {'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'}

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        video_data_script = None
        for script in scripts:
            if 'ytInitialData' in str(script):
                video_data_script = str(script)
                break

        if not video_data_script:
            return []

        json_match = re.search(r'var ytInitialData = ({.*?});', video_data_script)
        if not json_match:
            return []

        data = json.loads(json_match.group(1))

        video_list = []
        try:
            contents = \
                data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
                    'contents'][0][
                    'itemSectionRenderer']['contents']

            for content in contents:
                video_renderer = content.get('videoRenderer')
                if video_renderer:
                    title = video_renderer['title']['runs'][0]['text']
                    video_id = video_renderer['videoId']
                    link = f"https://www.youtube.com/watch?v={video_id}"

                    video_list.append({'title': title, 'link': link})
        except (KeyError, IndexError):
            return []

        return video_list

    except requests.exceptions.RequestException:
        return []


def get_all_videos():
    search_queries = [
        '이무진',
        '이무진 라이브',
        '이무진 리무진서비스',
        'Lee Mujin',
        '이무진 노래',
        '이무진 출근길',
        '이무진 불후의명곡',
        '이무진 커버',
        'Lee Mujin live',
        '이무진 콘서트',
        '이무진 아이유',
        '이무진 인터뷰',
        '이무진 유튜브',
        'Lee Mujin song',
        '이무진 OST',
        '이무진 레전드',
        '이무진 2024',
        'Lee Mujin cover',
        '이무진 감동',
        '이무진 최신'
    ]

    all_videos = {}
    for query in search_queries:
        videos = get_search_results(query)
        for video in videos:
            all_videos[video['link']] = video

    return list(all_videos.values())


def classify_videos(video_list):
    classified_videos = {
        'songs': [],
        'commute': [],
        'entertainment': [],
        'etc': []
    }

    commute_keywords = ['출근', '퇴근', '출퇴근', '출퇴근길', '공항']
    entertainment_keywords = ['예능', 'TV', '방송', '예능편', 'EP', '비하인드', 'Behind', '인터뷰', '서비스']
    song_keywords = ['노래', '커버', '라이브', '무대', 'Live', '뮤직', 'Music', '음악', 'MV', '버스킹', '콘서트', 'Playlist']

    for video in video_list:
        title = video['title'].lower()

        if any(keyword in title for keyword in commute_keywords):
            classified_videos['commute'].append(video)
            continue
        if any(keyword in title for keyword in entertainment_keywords):
            classified_videos['entertainment'].append(video)
            continue
        if any(keyword in title for keyword in song_keywords):
            classified_videos['songs'].append(video)
            continue
        classified_videos['etc'].append(video)

    return classified_videos


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # URL 파싱
        path = urlparse(self.path).path
        query = urlparse(self.path).query

        try:
            if path == '/api/songs' or query == 'type=songs':
                all_videos = get_all_videos()
                if all_videos:
                    data_cache = classify_videos(all_videos)
                    response_data = data_cache['songs']
                else:
                    self.send_error_response(503, "데이터를 로드할 수 없습니다.")
                    return

            elif path == '/api/commute' or query == 'type=commute':
                all_videos = get_all_videos()
                if all_videos:
                    data_cache = classify_videos(all_videos)
                    response_data = data_cache['commute']
                else:
                    self.send_error_response(503, "데이터를 로드할 수 없습니다.")
                    return

            elif path == '/api/entertainment' or query == 'type=entertainment':
                all_videos = get_all_videos()
                if all_videos:
                    data_cache = classify_videos(all_videos)
                    response_data = data_cache['entertainment']
                else:
                    self.send_error_response(503, "데이터를 로드할 수 없습니다.")
                    return

            elif path == '/api/all' or query == 'type=all':
                all_videos = get_all_videos()
                if all_videos:
                    response_data = classify_videos(all_videos)
                else:
                    self.send_error_response(503, "데이터를 로드할 수 없습니다.")
                    return

            elif path == '/api/refresh_data' or query == 'type=refresh_data':
                all_videos = get_all_videos()
                if all_videos:
                    data_cache = classify_videos(all_videos)
                    response_data = {
                        "message": "데이터가 성공적으로 새로고침되었습니다.",
                        "total_videos": len(all_videos),
                        "songs": len(data_cache['songs']),
                        "commute": len(data_cache['commute']),
                        "entertainment": len(data_cache['entertainment']),
                        "etc": len(data_cache['etc'])
                    }
                else:
                    self.send_error_response(500, "데이터를 새로고침하는 데 실패했습니다.")
                    return
            else:
                response_data = {
                    "message": "LeeMujin API",
                    "endpoints": [
                        "/api/songs",
                        "/api/commute",
                        "/api/entertainment",
                        "/api/all",
                        "/api/refresh_data"
                    ]
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error_response(500, f"오류가 발생했습니다: {str(e)}")

    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"message": message}, ensure_ascii=False).encode('utf-8'))