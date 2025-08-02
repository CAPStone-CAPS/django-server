from django.contrib import admin
from .models import AIDailySummary

# Register your models here.
@admin.register(AIDailySummary)
class AIDailySummaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'created_at')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'message')
    ordering = ('-date',)