from django.db import migrations, models

# 旧カテゴリ → 新カテゴリ。経験談・個人開発・チーム開発はいずれも「開発の記録と学び」へ寄せる。
# 内容が合わない記事は管理画面(/admin/)で個別に付け替える。
OLD_TO_NEW = {
    'experience': 'dev',
    'personal': 'dev',
    'team': 'dev',
}


def forwards(apps, schema_editor):
    NoteArticle = apps.get_model('core', 'NoteArticle')
    for old, new in OLD_TO_NEW.items():
        NoteArticle.objects.filter(category=old).update(category=new)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_notearticle_thumbnail_url_alter_notearticle_summary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notearticle',
            name='category',
            field=models.CharField(
                choices=[
                    ('self', '自己・業界・企業理解'),
                    ('dev', '開発の記録と学び'),
                    ('event', '就活イベント・インターンでの振り返り'),
                    ('topic', '時事・興味の考察'),
                ],
                default='dev',
                help_text='noteの記事タイトル先頭の接頭辞（例: 【開発の記録と学び】）から自動判定',
                max_length=20,
            ),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
