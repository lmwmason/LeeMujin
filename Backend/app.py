from flask import Flask, jsonify
from youtube_crawler import get_all_videos, classify_videos

app = Flask(__name__)

data_cache = None

@app.route('/')
def home():
    return "LeeMujin api"

@app.route('/refresh_data', methods=['GET'])
def refresh_data():
    global data_cache
    all_videos = get_all_videos()
    if all_videos:
        data_cache = classify_videos(all_videos)
        return jsonify({"message": "데이터가 성공적으로 새로고침되었습니다."})
    else:
        return jsonify({"message": "데이터를 새로고침하는 데 실패했습니다."}, 500)

@app.route('/songs', methods=['GET'])
def get_songs():
    if data_cache is None:
        return jsonify({"message": "데이터가 아직 로드되지 않았습니다. /refresh_data를 먼저 요청해주세요."}, 503)
    return jsonify(data_cache['songs'])

@app.route('/commute', methods=['GET'])
def get_commute():
    if data_cache is None:
        return jsonify({"message": "데이터가 아직 로드되지 않았습니다. /refresh_data를 먼저 요청해주세요."}, 503)
    return jsonify(data_cache['commute'])

@app.route('/entertainment', methods=['GET'])
def get_entertainment():
    if data_cache is None:
        return jsonify({"message": "데이터가 아직 로드되지 않았습니다. /refresh_data를 먼저 요청해주세요."}, 503)
    return jsonify(data_cache['entertainment'])

if __name__ == '__main__':
    all_videos = get_all_videos()
    if all_videos:
        data_cache = classify_videos(all_videos)

    app.run(debug=True)