from django.contrib import admin
from apps.accounts.models import Role, Employee, Customer


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    search_fields = ("title",)
    ordering = ("title",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "role",
        "balance",
        "mobile",
        "status",
    )

    search_fields = (
        "first_name",
        "last_name",
        "mobile",
    )

    list_filter = (
        "role",
        "status",
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "subscription_code",
        "name",
        "balance",
        "mobile",
        "address"
    )

    search_fields = (
        "subscription_code",
        "name",
        "mobile",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "-balance",
    )

