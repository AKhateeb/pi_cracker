from django.urls import path
from . import views

app_name = "instagram"

urlpatterns = [
    path('', views.index, name='index'),
    path('set_username', views.set_username, name='set_username'),
    path('check', views.check_status, name='check_status'),
    path('parse', views.parse_state, name='parse_state'),
]