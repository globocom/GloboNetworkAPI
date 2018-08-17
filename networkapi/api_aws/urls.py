# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_aws import views

urlpatterns = patterns(
    'networkapi.api_aws.views',
    url(r'^v3/aws/vpc((?P<vrf_ids>[;\w]+)/)?$',
        views.AwsVpcView.as_view()),

)
