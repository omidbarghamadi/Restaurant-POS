from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_type",
        "amount",
        "payment_method",
        "employee",
        "customer",
        "transaction_date",
    )

    list_filter = (
        "transaction_type",
        "payment_method",
        "transaction_date",
    )

    search_fields = (
        "description",
        "employee__user__username",
        "customer__name",
    )

    ordering = (
        "-transaction_date",
    )

    fieldsets = (
        (
            "اطلاعات تراکنش",
            {
                "fields": (
                    "transaction_type",
                    "amount",
                    "payment_method",
                    "transaction_date",
                ),
            },
        ),
        (
            "طرف تراکنش",
            {
                "fields": (
                    "employee",
                    "customer",
                ),
            },
        ),
        (
            "اطلاعات پرداخت",
            {
                "fields": (
                    "description",
                ),
            },
        ),
    )
