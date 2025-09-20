import requests
from bs4 import BeautifulSoup
import re
import json


def get_search_results(query):
    base_url = "https://www.youtube.com/results"
    params = {'search_query': query}
    headers = {'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'}

    try:
        response = requests.get(base_url, params=params, headers=headers)
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
            data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0][
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
        # 1-5: 기본 핵심 검색어 (가장 많이 검색되는)
        '이무진',
        '이무진 라이브',
        '이무진 리무진서비스',
        'Lee Mujin',
        '이무진 노래',

        # 6-10: 인기 프로그램/콘텐츠
        '이무진 출근길',
        '이무진 불후의명곡',
        '이무진 커버',
        'Lee Mujin live',
        '이무진 콘서트',

        # 11-15: 협업/화제 검색어
        '이무진 아이유',
        '이무진 인터뷰',
        '이무진 유튜브',
        'Lee Mujin song',
        '이무진 OST',

        # 16-20: 트렌드/감정 검색어
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
            # 링크를 키로 사용하여 중복을 제거합니다.
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


if __name__ == '__main__':
    all_videos = get_all_videos()
    if all_videos:
        classified = classify_videos(all_videos)
        print("--- 총 크롤링된 영상 수 ---")
        print("총 영상:", len(all_videos), "건")
        print("\n--- 분류 결과 ---")
        print("노래:", len(classified['songs']), "건")
        print("출퇴근:", len(classified['commute']), "건")
        print("예능:", len(classified['entertainment']), "건")
        print("기타:", len(classified['etc']), "건")