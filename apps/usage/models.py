from django.db import models
from django.contrib.auth.models import User

class AppInfo(models.Model):
    package_name = models.CharField(max_length=255, unique=True)
    app_name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.app_name} ({self.package_name})"

class UsageRecord(models.Model):
    class UsageRecord(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usage_records")
        app = models.ForeignKey(AppInfo, on_delete=models.CASCADE, related_name="usage_records")
        usage_time_ms = models.BigIntegerField()
        start_time = models.BigIntegerField()
        end_time = models.BigIntegerField()
        created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = []