from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'profile_image']
    search_fields = ['user__username']
    ordering = ['user__username']
    
    def has_add_permission(self, request):
        return False
