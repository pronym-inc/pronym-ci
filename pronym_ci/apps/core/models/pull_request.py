from enum import Enum

from django.db import models


class PullRequestStatus(Enum):
    PENDING = 'pending'
    FAILED = 'failed'
    ERROR = 'error'
    SUCCESS = 'success'


STATUS_CHOICES = (
    (PullRequestStatus.PENDING.name, 'Pending'),
    (PullRequestStatus.FAILED.name, 'Failed'),
    (PullRequestStatus.ERROR.name, 'Error'),
    (PullRequestStatus.SUCCESS.name, 'Success')
)


class PullRequest(models.Model):
    name = models.CharField(max_length=255, unique=True)
    repository = models.ForeignKey('Repository', on_delete=models.CASCADE, related_name='pull_requests')
    pr_number = models.PositiveIntegerField()
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=PullRequestStatus.PENDING.name)
