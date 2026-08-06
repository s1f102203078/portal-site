from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.TopView.as_view(), name='top'),
    path('sync/', views.sync_webhook, name='sync_webhook'),
]
