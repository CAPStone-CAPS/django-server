from django.db import models
from django.contrib.auth.models import User

"""
 AI 데일리 요약 DB 구조
- | id (PK, INT) | user (FK) | message (TEXT) | date (DATE) |
"""

class AIDailySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_summaries')
    message = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"