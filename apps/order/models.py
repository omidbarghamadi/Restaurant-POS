from django.db import models
from django.utils import timezone

from apps.accounts.models import Customer
from apps.menu.models import MenuItem


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

    # class Status(models.TextChoices):
    #     PENDING = "pending", "در انتظار"
    #     PREPARING = "preparing", "در حال آماده سازی"
    #     READY = "ready", "آماده تحویل"
    #     COMPLETED = "completed", "تحویل شده"
    #     CANCELED = "canceled", "لغو شده"

    # class OrderType(models.TextChoices):
    #     DINE_IN = "dine_in", "سالن"
    #     TAKEAWAY = "takeaway", "بیرون بر"
    #     DELIVERY = "delivery", "ارسال"

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

    # cashier = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.PROTECT,
    #     related_name="orders",
    #     verbose_name="صندوق دار",
    # )

    # status = models.CharField(
    #     max_length=20,
    #     choices=Status.choices,
    #     default=Status.PENDING,
    #     verbose_name="وضعیت",
    # )

    order_type = models.ForeignKey(
        OrderType,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="نوع سفارش",
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

    tax = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مالیات",
    )

    packaging_cost = models.PositiveBigIntegerField(
        default=0,
        verbose_name="هزینه بسته‌بندی",
    )

    total_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مبلغ کل",
    )

    order_date = models.DateField(
        default=timezone.localdate,
        verbose_name="تاریخ سفارش"
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
    