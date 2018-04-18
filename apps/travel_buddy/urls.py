# App [travel_buddy] Routing File

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^logreg$', views.logreg),
    url(r'^register$', views.registration),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^travels$', views.travels),
    url(r'^travels/new$', views.new_plan),
    url(r'^travels/add$', views.add_plan), 
    url(r'^travels/join/(?P<plan_id>\d+)$', views.join_plan),
    url(r'^travels/destination/(?P<plan_id>\d+)$', views.view_plan),
]