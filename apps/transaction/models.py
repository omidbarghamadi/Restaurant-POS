from django.conf import settings
from django.db import models


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        SALARY = "salary", "پرداخت حقوق"
        RECEIVABLE = "receivable", "دریافت طلب"
        EXPENSE = "expense", "هزینه"
        RAW_MATERIAL = "raw_material", "خرید مواد اولیه"
        REPAIR = "repair", "تعمیرات"
        DAMAGE = "damage", "خسارت"
        DELIVERY = "delivery", "پیک"
        WITHDRAWAL = "withdrawal", "برداشت"
        OTHER_INCOME = "other_income", "سایر درآمدها"
        OTHER_EXPENSE = "other_expense", "سایر هزینه‌ها"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "نقدی"
        CARD = "card", "کارت بانکی"
        CARD_TO_CARD = "card_to_card", "کارت به کارت"
        OTHER = "other", "سایر"

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name="نوع تراکنش",
    )

    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD_TO_CARD,
        null=True,
        blank=True,
        verbose_name="روش پرداخت",
    )

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.PROTECT,
        related_name="transactions",
        blank=True,
        null=True,
        verbose_name="کارمند",
    )

    customer = models.ForeignKey(
        "accounts.Customer",
        on_delete=models.PROTECT,
        related_name="transactions",
        blank=True,
        null=True,
        verbose_name="مشتری",
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="توضیحات",
    )

    transaction_date = models.DateTimeField(
        verbose_name="تاریخ تراکنش",
    )

    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="paid_transactions",
        verbose_name="پرداخت کننده",
    )

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"
        ordering = ("-transaction_date",)

    def __str__(self):
        return (
            f"{self.get_transaction_type_display()} - "
            f"{self.amount}"
        )
