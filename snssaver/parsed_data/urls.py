from django.conf.urls import url
from django.urls import path
from . import views

# <slug:ids>
# url(r'^change_line_chart/$', views.change_line_chart, name='change_line_chart'),
# url(r'^auto_id/$', views.auto_id, name="auto_id"),
# (?P<ids>[a-zA-Z0-9._]+)/
# (?P<page>[0-9]+)
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search_user/$', views.search_user, name="search_user"),
    url(r'^analysis/$', views.analysis, name="analysis"),
    url(r'^gallery/(?P<ids>[a-zA-Z0-9._]+)/$', views.gallery, name="gallery"),
    url(r'^video/(?P<ids>[a-zA-Z0-9._]+)/$', views.video, name="video"),
]