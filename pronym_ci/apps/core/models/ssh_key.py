from django.db import models


class SshKey(models.Model):
    name = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
