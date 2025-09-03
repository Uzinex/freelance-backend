from django.contrib import admin
from .models import Room, Message

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "created_at")
    search_fields = ("project__title",)
    list_filter = ("created_at",)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "author", "created_at")
    search_fields = ("room__id", "author__username", "content")
    list_filter = ("created_at",)
