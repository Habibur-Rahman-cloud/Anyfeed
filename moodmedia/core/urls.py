from django.urls import path
from core import views
from .views import login_view
from .views import GooglePasswordChangeView

urlpatterns = [
    path('', views.home, name='home'),  # Mood grid
    path('feed/<slug:mood>/', views.mood_feed, name='mood_feed'),  # Mood-specific content
    path('dashboard/', views.dashboard, name='dashboard'),
    path('feed/', views.feed_view, name='feed'),  # <- name must be 'feed'
    path('search/', views.search_results, name='search_results'),
    path('login/', login_view, name='login'),
    path('google-signup-form/', views.google_signup_form, name='google_signup_form'),
    path('accounts/password/change/', GooglePasswordChangeView.as_view(), name='account_change_password'),
    path('feed/<str:mood>/', views.mood_feed, name='mood_feed'),
    path('api/videos/<str:mood>/', views.video_api, name='video_api'),
    # ✅ API endpoint to fetch videos
    path('api/youtube/<slug:mood>/', views.youtube_api_view, name='youtube_api'),
]
