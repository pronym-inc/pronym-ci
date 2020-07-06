import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from django.conf import settings
from git import Repo

from pronym_ci.apps.core.models import PullRequest
from pronym_ci.apps.core.models.build import Build
from pronym_ci.apps.core.models.pull_request import PullRequestStatus
from pronym_ci.apps.core.models.repository import PythonVersion
from pronym_ci.apps.core.models.ssh_key import SshKey

logger = logging.getLogger('pronym_ci')


class PullRequestBuildService:
    """A service responsible for building pull requests and assigning them a status."""

    def build_pull_request(self, pull_request: PullRequest) -> PullRequestStatus:
        unit_test_status: Optional[PullRequestStatus] = None
        integration_status: Optional[PullRequestStatus] = None
        api_integration_status: Optional[PullRequestStatus] = None
        wdio_status: Optional[PullRequestStatus] = None
        if pull_request.repository.run_unittests:
            unit_test_status = self.run_unit_tests(pull_request)
        if pull_request.repository.run_integration_tests:
            integration_status = self.run_integration_tests(pull_request)
        if pull_request.repository.run_api_integration_tests:
            api_integration_status = self.run_api_integration_tests(pull_request)
        if pull_request.repository.run_wdio_tests:
            wdio_status = self.run_wdio_tests(pull_request)

        found_statuses = [
            status
            for status
            in [unit_test_status, integration_status, api_integration_status, wdio_status]
            if status is not None
        ]
        # If there is a single error, return error.  Then if there is a single failure, likewise.  Then pending.
        status_order = [PullRequestStatus.ERROR, PullRequestStatus.FAILED, PullRequestStatus.PENDING]
        for status in status_order:
            if status in found_statuses:
                return status
        return PullRequestStatus.SUCCESS

    def run_unit_tests(self, pull_request: PullRequest) -> Build:
        """Run the unit tests for the given PR."""
        # First, we need to setup the virtuale env.
        path = self._setup_virtualenv(pull_request)
        repo = Repo(str(path))
        sha = repo.head.commit.hexsha
        venv_path = os.path.join(str(path), 'venv')
        pytest_path = os.path.join(venv_path, 'bin', 'pytest')
        tests_path = os.path.join(str(path), pull_request.repository.name, 'tests')
        # Run the unit tests.
        completed_process: subprocess.CompletedProcess = subprocess.run(
            [
                pytest_path,
                tests_path
            ],
            capture_output=True,
            env={
                'DJANGO_SETTINGS_MODULE': f'{pull_request.repository.name}.conf.environments.local',
                'PYTHONPATH': str(path)
            }
        )
        # Return a build object.
        build = Build.objects.create(
            pull_request=pull_request,
            status=
            PullRequestStatus.SUCCESS.value
            if completed_process.returncode == 0 else
            PullRequestStatus.FAILED.value,
            stdout=completed_process.stdout,
            stderr=completed_process.stderr,
            commit=sha
        )
        return build

    def run_integration_tests(self, pull_request: PullRequest) -> Build:
        """Run the integration tests for the given PR."""
        # Set up the vagrant machine.
        self._setup_vagrant(pull_request)

    def run_api_integration_tests(self, pull_request: PullRequest) -> Build:
        """Run the API integration tests for the given PR."""

    def run_wdio_tests(self, pull_request: PullRequest) -> Build:
        """Run the webdriverio tests for the given PR."""

    def _clone_and_refresh_pull_request(self, pull_request: PullRequest) -> Path:
        repo_path = os.path.join(settings.REPO_BASE_PATH, str(pull_request.id))
        remote_branch_name = f'pull/{pull_request.pr_number}/head'
        if os.path.exists(repo_path):
            repo = Repo(repo_path)
            repo.git.pull('origin', remote_branch_name)
        else:
            local_branch_name = f'pr-{pull_request.id}'
            repo = Repo.clone_from(
                pull_request.repository.url,
                repo_path
            )
            repo.git.fetch('origin', f'{remote_branch_name}:{local_branch_name}')
            repo.git.checkout(local_branch_name)
        return Path(repo_path)

    def _setup_vagrant(self, pull_request: PullRequest) -> Path:
        # Move in the SSH key.
        deploy_path = os.path.join(settings.REPO_BASE_PATH, f'deploy-{pull_request.id}')
        if os.path.exists(deploy_path):
            repo = Repo(deploy_path)
            repo.git.pull()
        else:
            Repo.clone_from(
                pull_request.repository.url,
                deploy_path,
                multi_options=[
                    f'--branch={pull_request.repository.deployment_branch}'
                ]
            )
        with open(os.path.join(deploy_path, 'git_ssh_key'), 'w') as f:
            f.write(pull_request.repository.ssh_key.content.strip())
        completed_process: subprocess.CompletedProcess = subprocess.run([
            'vagrant',
            'up'
        ], cwd=deploy_path)
        if completed_process.returncode != 0:
            raise Exception("Failed to set up vagrant.")
        return Path(deploy_path)

    def _setup_virtualenv(self, pull_request: PullRequest) -> Path:
        repo_path = self._clone_and_refresh_pull_request(pull_request)
        pip_executable: str
        python_executable: str
        if pull_request.repository.python_version == PythonVersion.PYTHON_3_8:
            pip_executable = 'pip3.8'
            python_executable = 'python3.8'
        else:
            logger.warning(f"Unknown Python version: {pull_request.repository.python_version}")
            pip_executable = 'pip3.8'
            python_executable = 'python3.8'
        # Create virtualenv.
        venv_path = os.path.join(str(repo_path), 'venv')
        python_path = os.path.join(settings.VIRTUALENV_DIR, 'bin', python_executable)
        if not os.path.exists(venv_path):
            completed_venv_process: subprocess.CompletedProcess = subprocess.run([
                python_path,
                '-m',
                'venv',
                venv_path
            ])
            if completed_venv_process.returncode != 0:
                raise Exception("Failed to create virtualenv.")
        pip_path = os.path.join(venv_path, 'bin', pip_executable)
        requirements_path = os.path.join(str(repo_path), 'requirements.txt')
        completed_process: subprocess.CompletedProcess = subprocess.run([
            pip_path,
            'install',
            '-r',
            requirements_path,
            '--upgrade'
        ])
        if completed_process.returncode != 0:
            raise Exception("Failed to install pip requirements.")
        return repo_path
