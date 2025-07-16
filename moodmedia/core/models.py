from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Custom User Model
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)  # from Google

# Video Model
class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField()
    mood = models.CharField(max_length=100)
    published_at = models.DateTimeField()
    view_count = models.IntegerField()

    def __str__(self):
        return self.title

# User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True, default='temp_username')
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)  # Google avatar fallback
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Custom upload
    google_signup_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username