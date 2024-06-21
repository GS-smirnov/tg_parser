import uuid

from parser_app.models import Channels
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Заполняет таблицу channels'

    def handle(self, *args, **options):
        channels = [
            'investfuture',
            'IF_adv',
            'tb_invest_official',
            'AK47pfl',
            'finamalert',
            'omyinvestments',
            'lemonfortea',
            'investingcorp',
            'alfa_investments',
            'SberInvestments',
        ]

        for channel in channels:
            Channels.objects.update_or_create(
                channel=channel,
                defaults={
                    'uuid': uuid.uuid4(),
                }
            )

        self.stdout.write(self.style.SUCCESS('Данные для таблицы channels успешно добавлены.'))
