import logging
from typing import Dict, Any, Optional, Union

from pronym_api.models import ApiAccountMember
from pronym_api.views.actions import BaseAction, NoResourceAction, NullResource, ApiProcessingFailure
from pronym_api.views.api_view import NoResourceApiView, HttpMethod
from pronym_api.views.validation import ApiValidationErrorSummary

from pronym_ci.apps.core.models import PullRequest, Repository
from pronym_ci.apps.core.tasks.run_unit_tests import run_unit_tests

logger = logging.getLogger("pronym_ci")


class PrRunUnitTestsAction(NoResourceAction):
    def execute(self, request: Dict[str, Any], account_member: Optional[ApiAccountMember],
                resource: NullResource = NullResource()) -> Optional[Union[ApiProcessingFailure, Dict[str, Any]]]:
        if 'pull_request' not in request:
            return {}
        try:
            repository = Repository.objects.get(name=request['repository']['name'])
        except Repository.DoesNotExist:
            logger.warning(f"Did not find matching repo for {request['repository']['name']}, doing nothing.")
            return {}
        try:
            pull_request = PullRequest.objects.get(pr_number=request['number'])
        except PullRequest.DoesNotExist:
            pull_request = PullRequest.objects.create(
                pr_number=request['number'],
                repository=repository,
                name=request['pull_request']['title']
            )
        run_unit_tests.delay(request['pull_request']['head']['sha'], pull_request.id)
        return {}

    def validate(self, request_data: Dict[str, Any], account_member: Optional[ApiAccountMember],
                 resource: NullResource = NullResource()) -> Union[ApiValidationErrorSummary, Dict[str, Any]]:
        return {}


class PrRunUnitTestsApiView(NoResourceApiView):

    def _get_action_configuration(self) -> Dict[HttpMethod, BaseAction]:
        return {
            HttpMethod.POST: PrRunUnitTestsAction()
        }

    def _get_endpoint_name(self) -> str:
        return 'pr-status'
