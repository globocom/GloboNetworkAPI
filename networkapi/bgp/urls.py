from django.conf.urls import patterns, url

from networkapi.bgp.resource.bgp_resource import BGPResource


resource = BGPResource()

urlpatterns = patterns('',
   url(r'^$', resource.handle_request, name='bgp.list'),
)
