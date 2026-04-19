from django.db import models
from django.contrib.auth.models import User

class BrowseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='browse_histories')
    dish_name = models.CharField(max_length=255)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.username} viewed {self.dish_name}"