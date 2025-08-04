from django.db import models
from django.contrib.auth.models import User

class AppInfo(models.Model):
    package_name = models.CharField(max_length=255, unique=True)
    app_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.app_name} ({self.package_name})"

class UsageRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usage_records", null=True)
    app = models.ForeignKey(AppInfo, on_delete=models.CASCADE, related_name="usage_records", null=True)
    usage_time_ms = models.BigIntegerField(null=True)
    start_time = models.BigIntegerField(null=True)
    end_time = models.BigIntegerField(null=True)
    memo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null= True)

    class Meta:
        ordering = []