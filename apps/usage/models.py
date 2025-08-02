from django.db import models
from django.contrib.auth.models import User

class UsageRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usage_records")
    package_name = models.CharField(max_length=255)
    app_name = models.CharField(max_length=255)
    usage_time_ms = models.BigIntegerField()
    start_time = models.BigIntegerField()  # 타임스탬프 밀리초 단위 저장
    end_time = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']