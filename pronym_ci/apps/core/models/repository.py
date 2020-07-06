from enum import Enum

from django.db import models
from pronym_api.models import ApiAccount


class PythonVersion(Enum):
    PYTHON_3_8 = '3.8'


class Repository(models.Model):
    PYTHON_VERSION_CHOICES = (
        (PythonVersion.PYTHON_3_8.name, '3.8'),
    )

    name = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(ApiAccount, on_delete=models.CASCADE, related_name='repositories')
    ssh_key = models.ForeignKey('SshKey', on_delete=models.CASCADE, related_name='+')
    python_version = models.CharField(max_length=255, choices=PYTHON_VERSION_CHOICES)
    deployment_repo = models.CharField(max_length=255, null=True, blank=True)
    deployment_branch = models.CharField(max_length=255, default="master")
    run_unittests = models.BooleanField()
    run_api_integration_tests = models.BooleanField()
    run_integration_tests = models.BooleanField()
    run_wdio_tests = models.BooleanField()

    def __str__(self) -> str:
        return self.name
