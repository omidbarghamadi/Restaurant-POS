from django.db import models


class Category(models.Model):
    title = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="نام دسته"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="وضعیت"
    )

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام آیتم"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="دسته بندی"
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="قابل سفارش"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    image = models.ImageField(
        upload_to="menu/",
        blank=True,
        null=True,
        verbose_name="تصویر"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "آیتم منو"
        verbose_name_plural = "آیتم های منو"

    def __str__(self):
        return self.name


class MenuItemVariant(models.Model):
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="آیتم منو"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="نام زیرمنو"
    )

    price = models.BigIntegerField(
        verbose_name="قیمت"
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="قابل سفارش"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    class Meta:
        ordering = ["menu_item", "id"]
        verbose_name = "زیرمنو"
        verbose_name_plural = "زیرمنوها"
        constraints = [
            models.UniqueConstraint(
                fields=["menu_item", "name"],
                name="unique_menu_item_variant"
            )
        ]

    def __str__(self):
        return f"{self.menu_item} - {self.name}"