from django.db import models
from django.conf import settings


class Role(models.Model):
    title = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        unique=True,
        verbose_name="عنوان نقش"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )

    class Meta:
        db_table = 'Role'
        verbose_name = "نقش"
        verbose_name_plural = "نقش‌ها"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Employee(models.Model):

    class EmploymentStatus(models.TextChoices):
        ACTIVE = "active", "فعال"
        INACTIVE = "inactive", "غیرفعال"
        # SUSPENDED = "suspended", "تعلیق"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee"
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="employees",
        verbose_name="نقش"
    )

    first_name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name="نام"
    )

    last_name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name="نام خانوادگی"
    )

    mobile = models.CharField(
        max_length=11,
        blank=False,
        null=False,
        verbose_name="موبایل"

    )

    national_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="کد ملی"
    )

    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="آدرس"
    )

    hire_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ استخدام"
    )

    balance = models.BigIntegerField(
        default=0,
        editable=False,
        verbose_name="مانده حساب"
    )

    status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
        verbose_name="وضعیت"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "کارمند"
        verbose_name_plural = "کارمندان"
        ordering = ["role", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Customer(models.Model):

    subscription_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="کد اشتراک"
    )

    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name="نام"
    )

    mobile = models.CharField(
        max_length=11,
        blank=False,
        null=False,
        unique=True,
        verbose_name="موبایل"
    )

    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name="تلفن"
    )

    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="آدرس"
    )

    balance = models.BigIntegerField(
        default=0,
        editable=False,
        verbose_name="مانده حساب"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتری‌ها"
        ordering = ["balance"]

    def __str__(self):
        return f"{self.subscription_code} {self.name}"
    