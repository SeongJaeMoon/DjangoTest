from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search_user/$', views.search_user, name="search_user"),
    url(r'^change_line/$', views.change_line, name="change_line"),
    url(r'^chatbot/make_reply/$', views.make_reply, name='make_reply'),
    url(r'^comment/(?P<ids>[a-zA-Z0-9._]+)/$', views.comment, name="comment"),
    url(r'^analysis/(?P<ids>[a-zA-Z0-9._]+)/$', views.analysis, name="analysis"),
    url(r'^gallery/(?P<ids>[a-zA-Z0-9._]+)/$', views.gallery, name="gallery"),
    url(r'^video/(?P<ids>[a-zA-Z0-9._]+)/$', views.video, name="video"),
    url(r'^chatbot/$', views.chatbot, name="chatbot"),
]