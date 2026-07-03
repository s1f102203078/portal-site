from django.views.generic import TemplateView


class TopView(TemplateView):
    template_name = 'core/top.html'