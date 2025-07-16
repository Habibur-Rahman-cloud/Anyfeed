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


# reddit

import praw
from django.conf import settings

def fetch_reddit_content():
    reddit = praw.Reddit(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET,
        user_agent=settings.REDDIT_USER_AGENT
    )

    content = []
    subreddit = reddit.subreddit("videos+funny+memes+todayilearned")
    for post in subreddit.hot(limit=10):
        if post.is_video:
            content.append({
                'type': 'reddit_video',
                'title': post.title,
                'video_url': post.media['reddit_video']['fallback_url'],
                'source': f'https://reddit.com{post.permalink}',
            })
        elif post.url.endswith(('.jpg', '.png')):
            content.append({
                'type': 'reddit_image',
                'title': post.title,
                'image_url': post.url,
                'source': f'https://reddit.com{post.permalink}',
            })
    return content
