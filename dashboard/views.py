from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class SummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/summary.html'