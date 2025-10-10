from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    """Команда для ожидания готовности базы данных"""

    def handle(self, *args, **options):
        self.stdout.write('Ожидание подключения к базе данных...')
        db_conn = None
        attempts = 0
        max_attempts = 30

        while attempts < max_attempts:
            try:
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(
                    self.style.SUCCESS('База данных доступна!')
                )
                return
            except OperationalError:
                attempts += 1
                self.stdout.write(
                    f'База данных не доступна, ожидание 2 секунды... (попытка {attempts}/{max_attempts})'
                )
                time.sleep(2)

        self.stdout.write(
            self.style.ERROR('Не удалось подключиться к базе данных после всех попыток')
        )
        exit(1)