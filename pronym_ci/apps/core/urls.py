from django.conf.urls import url
from pronym_api.api.get_token import GetTokenApiView

from pronym_ci.apps.core.api.pr_unit_tests import PrRunUnitTestsApiView


app_name = 'bnadmin'

urlpatterns = [
    url(r'^pr_unit_tests/$',
        PrRunUnitTestsApiView.as_view(),
        name="pr_unit_test"),
    url(r'^get_token/$', GetTokenApiView.as_view(), name='get-token')
]
