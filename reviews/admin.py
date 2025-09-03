from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "target", "project", "rating", "created_at")
    search_fields = ("author__username", "target__username", "project__title")
    list_filter = ("rating", "created_at")
