from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.TopView.as_view(), name='top'),
    path('learning/', views.LearningLogListView.as_view(), name='learning_list'),
]