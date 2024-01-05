from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^(?:(?P<pms_type>\w+)/)?$', views.pms, name='pms'),
]