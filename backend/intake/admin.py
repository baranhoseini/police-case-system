from django.contrib import admin
from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "status", "bad_submission_count", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "created_by__username", "created_by__email")
