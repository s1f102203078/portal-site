from decouple import config
from django.core.management.base import BaseCommand
from django.utils import timezone
from notion_client import Client

from budget.models import SyncLog, Transaction

# Notion側のプロパティ名(データベースの列名と一致させる)
PROP_TITLE = '内容'
PROP_DATE = '日付'
PROP_AMOUNT = '金額'
PROP_CATEGORY = 'ロールアップ'


class Command(BaseCommand):
    help = 'Notionの取引記録データベースと同期します'

    def handle(self, *args, **options):
        notion = Client(auth=config('NOTION_API_KEY'))
        data_source_id = config('NOTION_BUDGET_DATA_SOURCE_ID')

        synced_count = 0
        error_message = None

        try:
            has_more = True
            start_cursor = None

            while has_more:
                body = {'page_size': 100}
                if start_cursor:
                    body['start_cursor'] = start_cursor

                response = notion.request(
                    path=f'data_sources/{data_source_id}/query',
                    method='POST',
                    body=body,
                )

                for page in response['results']:
                    self._upsert_transaction(page)
                    synced_count += 1

                has_more = response.get('has_more', False)
                start_cursor = response.get('next_cursor')

            SyncLog.objects.create(
                source='notion_budget',
                status='success',
                synced_count=synced_count,
            )
            self.stdout.write(self.style.SUCCESS(f'{synced_count}件を同期しました'))

        except Exception as e:
            error_message = str(e)
            SyncLog.objects.create(
                source='notion_budget',
                status='failed',
                synced_count=synced_count,
                error_message=error_message,
            )
            self.stderr.write(self.style.ERROR(f'同期に失敗しました: {error_message}'))
            raise

    def _upsert_transaction(self, page):
        props = page['properties']
        notion_page_id = page['id']

        title_list = props[PROP_TITLE]['title']
        memo = title_list[0]['plain_text'] if title_list else ''

        date_value = props[PROP_DATE]['date']
        date = date_value['start'] if date_value else None

        amount = props[PROP_AMOUNT]['number'] or 0

        category = self._extract_rollup_text(props[PROP_CATEGORY])

        Transaction.objects.update_or_create(
            notion_page_id=notion_page_id,
            defaults={
                'date': date,
                'category': category,
                'amount': int(amount),
                'memo': memo,
                'synced_at': timezone.now(),
            },
        )

    def _extract_rollup_text(self, rollup_prop):
        rollup = rollup_prop['rollup']
        if rollup['type'] != 'array':
            return ''

        items = rollup['array']
        if not items:
            return ''

        first = items[0]
        if first['type'] == 'title' and first['title']:
            return first['title'][0]['plain_text']
        return ''