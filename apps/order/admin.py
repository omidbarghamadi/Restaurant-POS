from django.contrib import admin

from .models import (
    DailyOrderCounter,
    Order,
    OrderItem,
    OrderType,
)


@admin.register(OrderType)
class OrderTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "order_type",
        "table_number",
        "total_price",
        "created_at",
    )

    list_filter = (
        "order_date",
        "order_type",
        "created_at",
    )

    search_fields = (
        "order_number",
        "order_type__name",
        "customer__first_name",
        "customer__last_name",
        "customer__mobile",
    )

    readonly_fields = (
        "order_date",
        "order_number",
        "created_at",
        "updated_at",
    )

    inlines = (
        OrderItemInline,
    )

    ordering = (
        "-created_at",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "menu_item",
        "quantity",
        "unit_price",
        "total_price",
        "note",
    )

    search_fields = (
        "menu_item__name",
        "order__order_number",
    )

    list_filter = (
        "order__order_date",
    )


@admin.register(DailyOrderCounter)
class DailyOrderCounterAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "last_number",
    )

    search_fields = (
        "date",
    )

    readonly_fields = (
        "date",
        "last_number",
    )

    ordering = (
        "-date",
    )