from django.db import models
from django.utils import timezone

from apps.accounts.models import Customer, Employee
from apps.menu.models import MenuItem, MenuItemVariant


def current_time():
    """ساعت فعلی (بدون ثانیه) به وقت محلی؛ مقدار پیش‌فرض ساعت سفارش."""
    return timezone.localtime().time().replace(second=0, microsecond=0)


class OrderType(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نوع سفارش"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="وضعیت"
    )

    class Meta:
        verbose_name = "نوع سفارش"
        verbose_name_plural = "نوع‌های سفارش"

    def __str__(self):
        return self.name


class Order(models.Model):

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "نقدی"
        CARD = "card", "کارتخوان"
        CARD_TO_CARD = "card_to_card", "کارت به کارت"
        ONLINE = "online", "آنلاین"
        CREDIT = "credit", "نسیه"
        COMBINED = "combined", "ترکیبی"
        FREE = "free", "رایگان"

    # class PaymentStatus(models.TextChoices):
    #     UNPAID = "unpaid", "پرداخت نشده"
    #     PAID = "paid", "پرداخت شده"

    order_number = models.PositiveIntegerField(
        verbose_name="شماره سفارش"
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="مشتری",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="کارمند",
    )

    order_type = models.ForeignKey(
        OrderType,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="نوع سفارش",
    )

    table_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="شماره میز",
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات",
    )

    discount = models.PositiveBigIntegerField(
        default=0,
        verbose_name="تخفیف",
    )

    delivery = models.PositiveBigIntegerField(
        default=0,
        verbose_name="هزینه پیک",
    )

    packaging_cost = models.PositiveBigIntegerField(
        default=0,
        verbose_name="هزینه بسته‌بندی",
    )

    total_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مبلغ کل",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
        null=True,
        blank=True,
        verbose_name="نوع پرداخت",
    )

    # payment_status = models.CharField(
    #     max_length=20,
    #     choices=PaymentStatus.choices,
    #     default=PaymentStatus.UNPAID,
    #     verbose_name="وضعیت پرداخت",
    # )

    order_date = models.DateField(
        default=timezone.localdate,
        verbose_name="تاریخ سفارش"
    )

    order_time = models.TimeField(
        default=current_time,
        verbose_name="ساعت سفارش",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ ویرایش",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        constraints = [
            models.UniqueConstraint(
                fields=["order_date", "order_number"],
                name="unique_order_number_per_day"
            )
        ]

    def __str__(self):
        return f"سفارش #{self.order_number}"


class DailyOrderCounter(models.Model):
    date = models.DateField(
        unique=True,
        verbose_name="تاریخ"
    )

    last_number = models.PositiveIntegerField(
        default=99,
        verbose_name="آخرین شماره سفارش"
    )

    class Meta:
        verbose_name = "شمارنده روزانه سفارش"
        verbose_name_plural = "شمارنده‌های روزانه سفارش"

    def __str__(self):
        return f"{self.date} - {self.last_number}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    # زیرمنوی انتخاب‌شده (قیمت واقعی از همینجا خوانده می‌شود).
    # nullable گذاشته شده تا migration بدون نیاز به backfill دیتای
    # قدیمی اجرا شود؛ اما در فرم به صورت الزامی اعتبارسنجی می‌شود.
    variant = models.ForeignKey(
        MenuItemVariant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="زیرمنو",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد",
    )

    unit_price = models.PositiveBigIntegerField(
        verbose_name="قیمت واحد",
    )

    total_price = models.PositiveBigIntegerField(
        verbose_name="جمع",
    )

    note = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="توضیحات",
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.menu_item.name} × {self.quantity}"