from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "is_verified", "is_staff", "date_joined"]
    search_fields = ["username", "email"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "current_title", "target_role", "years_experience"]
    search_fields = ["user__email", "full_name"]
