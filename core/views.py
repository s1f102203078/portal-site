import hmac

from decouple import config
from django.core.management import call_command
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from .models import NoteArticle


class TopView(TemplateView):
    template_name = 'core/top.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles_by_category'] = {
            key: NoteArticle.objects.filter(category=key)
            for key, _ in NoteArticle.CATEGORY_CHOICES
        }
        return context


@csrf_exempt
@require_POST
def sync_webhook(request):
    provided_token = request.headers.get('X-Sync-Token', '')
    expected_token = config('SYNC_SECRET_TOKEN')

    if not hmac.compare_digest(provided_token, expected_token):
        return JsonResponse({'error': 'unauthorized'}, status=401)

    try:
        call_command('sync_note')
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
