from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.SummaryView.as_view(), name='summary'),
    path('budget/', views.BudgetListView.as_view(), name='budget_list'),
]