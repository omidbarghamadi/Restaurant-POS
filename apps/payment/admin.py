from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "method",
        "amount",
        "payment_date",
    )

    list_filter = (
        "method",
        "payment_date",
    )

    search_fields = (
        "order__order_number",
        "note",
    )

    ordering = (
        "-payment_date",
    )

    readonly_fields = (
        "payment_date",
    )
