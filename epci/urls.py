from django.conf.urls import patterns, url

from .views import get_epci_boundary

urlpatterns = patterns('',
    url(r'^get-boundary/$', get_epci_boundary , name='get-epci-boundary'),
)
