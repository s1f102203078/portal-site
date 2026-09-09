import hmac
import json

from decouple import config
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
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
        payload = json.loads(request.body)
        articles = payload.get('articles', [])

        synced_count = 0
        for item in articles:
            NoteArticle.objects.update_or_create(
                url=item['url'],
                defaults={
                    'title': item['title'],
                    'summary': item.get('summary', ''),
                    'thumbnail_url': item.get('thumbnail_url', ''),
                    'category': item['category'],
                    'published_at': parse_datetime(item['published_at']),
                },
            )
            synced_count += 1

        return JsonResponse({'status': 'ok', 'synced_count': synced_count})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
