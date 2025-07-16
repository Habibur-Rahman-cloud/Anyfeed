from django.contrib import admin
from .models import UserProfile
from .models import CustomUser
from .models import Video

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(CustomUser)
admin.site.register(Video)
