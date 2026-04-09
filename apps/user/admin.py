# Register your models here.
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "nickname", "is_active", "is_admin", "created_at"]
    search_fields = ["email", "nickname"]
    list_filter = ["is_active", "is_staff"]
    readonly_fields = ["is_staff", "is_admin", "is_superuser"]
