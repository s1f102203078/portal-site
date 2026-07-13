from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    path('sync/', views.sync_webhook, name='sync_webhook'),
]