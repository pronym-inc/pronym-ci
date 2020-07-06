from json import dumps
from urllib.parse import urljoin

import requests
from django.conf import settings
from requests import Response


class ReportStatusService:
    """A service for communicating a status to GitHub for a build."""
    BASE_GITHUB_URL = 'https://api.github.com'

    def report_status(self, repository_name: str, commit_sha: str, status: str) -> Response:
        """Report the status to GitHub."""
        headers = {
            'Authorization': f'token {settings.GITHUB_AUTH_TOKEN}'
        }
        request_url = urljoin(
            self.BASE_GITHUB_URL,
            f'/repos/pronym-inc/{repository_name}/statuses/{commit_sha}'
        )
        data = {'state': status}
        response = requests.post(
            request_url,
            data=dumps(data),
            headers=headers
        )
        return response
