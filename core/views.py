from django.views.generic import TemplateView, ListView, DetailView
from .models import LearningLog


class TopView(TemplateView):
    template_name = 'core/top.html'


class LearningLogListView(ListView):
    model = LearningLog
    template_name = 'core/learning_list.html'
    context_object_name = 'logs'


class LearningLogDetailView(DetailView):
    model = LearningLog
    template_name = 'core/learning_detail.html'
    context_object_name = 'log'
