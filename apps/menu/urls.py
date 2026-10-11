from django.urls import path

from . import views


app_name = "menu"


urlpatterns = [

    # Category
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category-create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category-update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category-delete"),
    # Menu Item
    path("items/", views.MenuItemListView.as_view(), name="menu-item-list"),
    path("items/create/", views.MenuItemCreateView.as_view(), name="menu-item-create"),
    path("items/<int:pk>/edit/", views.MenuItemUpdateView.as_view(), name="menu-item-update"),
    path("items/<int:pk>/delete/", views.MenuItemDeleteView.as_view(), name="menu-item-delete"),
    # Variant
    path("variants/", views.MenuItemVariantListView.as_view(), name="variant-list"),
    path("variants/create/", views.MenuItemVariantCreateView.as_view(), name="variant-create"),
    path("variants/<int:pk>/edit/", views.MenuItemVariantUpdateView.as_view(), name="variant-update"),
    path("variants/<int:pk>/delete/", views.MenuItemVariantDeleteView.as_view(), name="variant-delete"),
]
