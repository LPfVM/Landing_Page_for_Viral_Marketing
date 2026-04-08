# Register your models here.
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "nickname", "is_active", "is_admin", "created_at"]
