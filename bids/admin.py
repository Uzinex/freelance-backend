from django.contrib import admin
from .models import Bid


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "freelancer", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("project__title", "freelancer__username")
