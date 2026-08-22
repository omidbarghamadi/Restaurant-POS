from django.db import models
from apps.order.models import Order


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "نقدی"
        CARD = "card", "کارت بانکی"
        CARD_TO_CARD = "card_to_card", "کارت به کارت"
        CREDIT = "credit", "نسیه"
        FREE = "free", "رایگان"
        STAFF_MEAL = "staff_meal", "غذای پرسنل"
        UNKNOWN = "unknown", "نامعلوم"

    # class PaymentStatus(models.TextChoices):
    #     PENDING = "pending", "در انتظار"
    #     COMPLETED = "completed", "موفق"
    #     CANCELLED = "cancelled", "لغو شده"
    #     REFUNDED = "refunded", "برگشت داده شده"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="سفارش",
    )

    method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.UNKNOWN,
        verbose_name="روش پرداخت",
    )

    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ",
    )

    # status = models.CharField(
    #     max_length=20,
    #     choices=PaymentStatus.choices,
    #     default=PaymentStatus.COMPLETED,
    #     verbose_name="وضعیت پرداخت",
    # )

    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="توضیحات",
    )

    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ پرداخت",
    )

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداختها"
        ordering = ("-payment_date",)

    def __str__(self):
        return f"{self.order} - {self.amount} - {self.get_method_display()}"