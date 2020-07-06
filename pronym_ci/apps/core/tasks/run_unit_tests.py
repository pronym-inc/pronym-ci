from celery import shared_task

from pronym_ci.apps.core.service.pull_request_build import PullRequestBuildService
from pronym_ci.apps.core.service.report_status import ReportStatusService


@shared_task
def run_unit_tests(commit_sha, pull_request_id):
    from pronym_ci.apps.core.models import PullRequest
    pr = PullRequest.objects.get(pk=pull_request_id)
    service = PullRequestBuildService()
    report_status_service = ReportStatusService()
    report_status_service.report_status(pr.repository.name, commit_sha, 'pending')
    build = service.run_unit_tests(pr)
    report_status_service.report_status(pr.repository.name, commit_sha, build.status)
