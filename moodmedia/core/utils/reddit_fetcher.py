import praw
from django.conf import settings

def fetch_reddit_posts(subreddit_name='motivation', limit=5):
    reddit = praw.Reddit(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET,
        user_agent=settings.REDDIT_USER_AGENT
    )

    posts = []
    try:
        for post in reddit.subreddit(subreddit_name).hot(limit=limit):
            if hasattr(post, 'media') and post.media and 'reddit_video' in post.media:
                posts.append({
                    "type": "reddit_video",
                    "title": post.title,
                    "video_url": post.media['reddit_video']['fallback_url'],
                    "source": f"https://reddit.com{post.permalink}"
                })
            elif post.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                posts.append({
                    "type": "reddit_image",
                    "title": post.title,
                    "image_url": post.url,
                    "source": f"https://reddit.com{post.permalink}"
                })
    except Exception as e:
        print("Reddit fetch error:", e)

    return posts
