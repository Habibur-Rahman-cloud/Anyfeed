import requests

def get_youtube_videos(mood, page_token=None):
    api_key = "AIzaSyDQpH00nog2MajipeEiytieaJAcZVFoAcU"  # 🔁 Replace this
    base_url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        'part': 'snippet',
        'q': mood,
        'type': 'video',
        'maxResults': 8,
        'key': api_key,
    }

    if page_token:
        params['pageToken'] = page_token

    response = requests.get(base_url, params=params)
    data = response.json()

    videos = []
    for item in data.get('items', []):
        video_id = item['id']['videoId']
        snippet = item['snippet']
        videos.append({
            'title': snippet['title'],
            'thumbnail': snippet['thumbnails']['medium']['url'],
            'videoId': video_id
        })

    return videos, data.get('nextPageToken')