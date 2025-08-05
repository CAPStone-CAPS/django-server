from django.contrib import admin
from .models import AppInfo, UsageRecord

@admin.register(AppInfo)
class AppInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'package_name', 'app_name']
    search_fields = ['package_name', 'app_name']
    ordering = ['app_name']
    
@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):   
    list_display = ['id', 'user', 'app', 'usage_time_ms', 'start_time', 'end_time', 'created_at']
    search_fields = ['user__username', 'app__app_name']
    list_filter = ['user', 'app']
    autocomplete_fields = ['user', 'app']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
