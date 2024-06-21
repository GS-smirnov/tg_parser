import uuid

from parser_app.models import Companies
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Заполняет таблицу companies'

    def handle(self, *args, **options):
        companies = [
            'сбер',
            'лукойл',
            'газпром',
            'яндекс',
            'мечел',
        ]

        for company in companies:
            Companies.objects.update_or_create(
                company=company,
                defaults={
                    'uuid': uuid.uuid4(),
                }
            )

        self.stdout.write(self.style.SUCCESS('Данные для таблицы companies успешно добавлены.'))
