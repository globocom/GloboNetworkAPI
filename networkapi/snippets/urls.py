from django.conf.urls import patterns, url

urlpatterns = patterns('networkapi.snippets.views',
    url(r'^snippets/$', 'snippet_list'),
)
