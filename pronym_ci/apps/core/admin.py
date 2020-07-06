from django.contrib import admin

from pronym_ci.apps.core.models import Repository, SshKey


admin.site.register(Repository)
admin.site.register(SshKey)
