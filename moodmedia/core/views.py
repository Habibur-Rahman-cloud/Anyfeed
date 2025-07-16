from django.shortcuts import render, redirect
from core.utils.yt_fetcher import get_youtube_videos
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import UserDashboardForm
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from allauth.socialaccount.models import SocialAccount
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Video
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Video
from googleapiclient.discovery import build
from django.conf import settings
from core.utils.reddit_fetcher import fetch_reddit_posts
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from core.models import Video
from django.db.models import Q


@login_required
def dashboard(request):
    user = request.user

    # Check if UserProfile exists, if not create it
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        username = request.POST.get('username')
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')

        profile.bio = bio
        profile.google_signup_complete = True  # or handle appropriately

        if avatar:
            profile.avatar = avatar

        if username and username != profile.username:
            if UserProfile.objects.exclude(pk=profile.pk).filter(username=username).exists():
                return render(request, 'dashboard.html', {
                    'profile': profile,
                    'username_error': "Username already taken."
                })
            profile.username = username

        profile.save()

    return render(request, 'dashboard.html', {'profile': profile})



def home(request):
    moods = [
        {'name': 'Motivation', 'slug': 'motivation', 'icon': 'fas fa-bolt'},
        {'name': 'Comedy', 'slug': 'comedy', 'icon': 'fas fa-laugh'},
        {'name': 'Music', 'slug': 'music', 'icon': 'fas fa-music'},
        {'name': 'Gaming', 'slug': 'gaming', 'icon': 'fas fa-gamepad'},
        {'name': 'Study', 'slug': 'study', 'icon': 'fas fa-book'},
        {'name': 'Sad', 'slug': 'sad', 'icon': 'fas fa-face-sad-tear'},
        {'name': 'Happy', 'slug': 'happy', 'icon': 'fas fa-face-smile'},
        {'name': 'Tech', 'slug': 'tech', 'icon': 'fas fa-microchip'},
        {'name': 'Trending', 'slug': 'trending', 'icon': 'fas fa-fire'},
        {'name': 'Workout', 'slug': 'workout', 'icon': 'fas fa-dumbbell'},
        {'name': 'Nature', 'slug': 'nature', 'icon': 'fas fa-tree'},
        {'name': 'Meditation', 'slug': 'meditation', 'icon': 'fas fa-spa'},
        {'name': 'Business', 'slug': 'business', 'icon': 'fas fa-briefcase'},
        {'name': 'News', 'slug': 'news', 'icon': 'fas fa-newspaper'},
        {'name': 'Learning', 'slug': 'learning', 'icon': 'fas fa-graduation-cap'},
        {'name': 'Finance', 'slug': 'finance', 'icon': 'fas fa-chart-line'},

    ]
    return render(request, 'pages/home.html', {'moods': moods})  # ✅ Fixed



def mood_feed(request, mood):
    moods = [
        {'name': 'Motivation', 'slug': 'motivation'},
        {'name': 'Comedy', 'slug': 'comedy'},
        {'name': 'Music', 'slug': 'music'},
        {'name': 'Gaming', 'slug': 'gaming'},
        {'name': 'Study', 'slug': 'study'},
        {'name': 'Sad', 'slug': 'sad'},
        {'name': 'Happy', 'slug': 'happy'},
        {'name': 'Tech', 'slug': 'tech'},
        {'name': 'Trending', 'slug': 'trending'},
        {'name': 'Workout', 'slug': 'workout'},
        {'name': 'Nature', 'slug': 'nature'},
        {'name': 'Meditation', 'slug': 'meditation'},
    ]
    return render(request, "pages/feed.html", {
        "mood": mood,
        "moods": moods
    })



def youtube_api_view(request, mood):
    language = request.GET.get("language", "")
    sort = request.GET.get("sort", "relevant")  # 🟢 Set default to "relevant"
    page_token = request.GET.get("pageToken", "")

    query = f"{mood} videos"
    if language:
        query += f" in {language}"

    yt_videos, next_token = fetch_youtube_videos(query, page_token, sort)
    reddit_posts = fetch_reddit_posts(subreddit_name=mood, limit=5)

    mixed = yt_videos + reddit_posts
    random.shuffle(mixed)

    return JsonResponse({
        "videos": mixed,
        "nextPageToken": next_token
    })


def search_results(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Video.objects.filter(
            title__icontains=query
        ) | Video.objects.filter(
            mood__icontains=query
        ) | Video.objects.filter(
            description__icontains=query
        )

    return render(request, 'search_results.html', {
        'query': query,
        'results': results
    })

@method_decorator(login_required, name='dispatch')
class GooglePasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not SocialAccount.objects.filter(user=request.user, provider='google').exists():
            messages.error(request, "You must sign up with Google to change your password.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Or your dashboard/feed
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def google_signup_form(request):
    return render(request, 'registration/google_signup_form.html')  # Create this template too


def video_api(request, mood):
    page = int(request.GET.get('page', 1))
    sort = request.GET.get('sort')

    videos = Video.objects.filter(mood=mood)

    if sort == "most_viewed":
        videos = videos.order_by("-view_count")
    elif sort == "latest":
        videos = videos.order_by("-published_at")
    elif sort == "oldest":
        videos = videos.order_by("published_at")

    paginator = Paginator(videos, 5)  # 5 videos per page
    page_obj = paginator.get_page(page)

    data = []
    for video in page_obj:
        data.append({
            'title': video.title,
            'description': video.description,
            'video_url': video.video_url,
            'mood': video.mood,
        })

    return JsonResponse({'videos': data})


def mood_feed(request, mood):
    sort = request.GET.get('sort')
    
    videos = Video.objects.filter(mood=mood)
    
    if sort == "most_viewed":
        videos = videos.order_by("-view_count")
    elif sort == "latest":
        videos = videos.order_by("-published_at")
    elif sort == "oldest":
        videos = videos.order_by("published_at")

    # Only load first 5 for initial load, rest via JS
    initial_videos = videos[:5]

    return render(request, "pages/feed.html", {
        "videos": initial_videos,
        "mood": mood
    })


YOUTUBE_API_KEY = "AIzaSyDQpH00nog2MajipeEiytieaJAcZVFoAcU"  # Replace with your actual key

def fetch_youtube_videos(query, page_token="", sort="relevance", max_results=10):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    sort_map = {
        "most_viewed": "viewCount",
        "latest": "date",
        "oldest": "date",
        "relevant": "relevance"
    }

    order = sort_map.get(sort, "relevance")

    try:
        search_response = youtube.search().list(
            q=query + " long video",
            type="video",
            part="snippet",
            maxResults=max_results,
            order=order,
            pageToken=page_token,
            videoDuration="long"
        ).execute()
    except Exception as e:
        print("YouTube API Error:", e)
        return [], ""

    videos = []
    for item in search_response.get("items", []):
        video = {
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
            "channel": item["snippet"]["channelTitle"],
            "video_url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
        }
        videos.append(video)

    next_token = search_response.get("nextPageToken", "")
    return videos, next_token

def feed_view(request):
    context = {}
    if request.user.is_authenticated:
        try:
            context['profile'] = request.user.userprofile
        except UserProfile.DoesNotExist:
            context['profile'] = None
    return render(request, "pages/feed.html", context)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()






    # ---------404 page view---------

    # core/views.py

def custom_404(request, exception):
    return render(request, 'pages/404.html', status=404)
