import hmac

from decouple import config
from django.core.management import call_command
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def sync_webhook(request):
    provided_token = request.headers.get('X-Sync-Token', '')
    expected_token = config('SYNC_SECRET_TOKEN')

    if not hmac.compare_digest(provided_token, expected_token):
        return JsonResponse({'error': 'unauthorized'}, status=401)

    try:
        call_command('sync_notion')
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    