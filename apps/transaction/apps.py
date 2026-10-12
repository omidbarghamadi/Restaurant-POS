from django.apps import AppConfig


class TransactionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.transaction'

    def ready(self):
        # ایمپورت اینجا لازمه تا سیگنال‌ها موقع بالا اومدن جنگو رجیستر بشن
        from . import signals  # noqa: F401
