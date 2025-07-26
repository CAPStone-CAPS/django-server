from django.contrib import admin
from .models import GroupInfo, UserGroupMembership

@admin.register(GroupInfo)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'group_name', 'description', 'create_date', 'modify_date']
    search_fields = ['group_name', 'description']
    list_filter = ['create_date']
    ordering = ['-create_date']

@admin.register(UserGroupMembership)
class UserGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'group']
    search_fields = ['user__username', 'group__group_name']
    list_filter = ['group']
    autocomplete_fields = ['user', 'group'] 
