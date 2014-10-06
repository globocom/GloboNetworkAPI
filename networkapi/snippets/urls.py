from django.conf.urls import patterns, url

urlpatterns = patterns('snippets.views',
    url(r'^snippets/$', 'snippet_list'),
)
