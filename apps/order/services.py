from django.db import transaction
from django.utils import timezone

from .models import DailyOrderCounter


@transaction.atomic
def get_next_order_number():
    today = timezone.localdate()

    counter, created = DailyOrderCounter.objects.select_for_update().get_or_create(
        date=today,
        defaults={"last_number": 99},
    )

    counter.last_number += 1
    counter.save(update_fields=["last_number"])

    return counter.last_number
