from django.contrib import admin
from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
    )

    ordering = (
        "title",
    )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "name",
        "price",
        "is_available",
    )

    list_filter = (
        "category",
        "is_available",
    )

    search_fields = (
        "name",
        "category__title",
    )

    autocomplete_fields = (
        "category",
    )

    ordering = (
        "category",
        "name",
    )
