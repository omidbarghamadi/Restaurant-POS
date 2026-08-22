from django.contrib import admin

from .models import Category, MenuItem, MenuItemVariant


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


class MenuItemVariantInline(admin.TabularInline):
    model = MenuItemVariant
    extra = 1

    fields = (
        "name",
        "price",
        "is_available",
        "is_active",
    )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "name",
        "is_available",
        "is_active",
    )

    list_filter = (
        "category",
        "is_available",
        "is_active",
    )

    search_fields = (
        "name",
        "category__title",
    )

    autocomplete_fields = (
        "category",
    )

    inlines = (
        MenuItemVariantInline,
    )

    ordering = (
        "category",
        "name",
    )


@admin.register(MenuItemVariant)
class MenuItemVariantAdmin(admin.ModelAdmin):
    list_display = (
        "menu_item",
        "name",
        "price",
        "is_available",
        "is_active",
    )

    list_filter = (
        "menu_item__category",
        "is_available",
        "is_active",
    )

    search_fields = (
        "name",
        "menu_item__name",
    )

    autocomplete_fields = (
        "menu_item",
    )

    ordering = (
        "menu_item",
        "name",
    )