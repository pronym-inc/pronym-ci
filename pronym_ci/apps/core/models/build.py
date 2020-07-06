from django.db import models

from pronym_ci.apps.core.models.pull_request import STATUS_CHOICES, PullRequestStatus


class Build(models.Model):
    pull_request = models.ForeignKey('PullRequest', on_delete=models.CASCADE, related_name='builds')
    datetime_created = models.DateTimeField(auto_now_add=True)
    commit = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=PullRequestStatus.PENDING.name)
    stdout = models.TextField()
    stderr = models.TextField()
