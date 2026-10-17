from django.urls import path

from . import views


app_name = "menu"


urlpatterns = [

    # Category
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
    # Menu Item
    path("items/", views.MenuItemListView.as_view(), name="menu_item_list"),
    path("items/create/", views.MenuItemCreateView.as_view(), name="menu_item_create"),
    path("items/<int:pk>/edit/", views.MenuItemUpdateView.as_view(), name="menu_item_update"),
    path("items/<int:pk>/delete/", views.MenuItemDeleteView.as_view(), name="menu_item_delete"),
    # Variant
    path("variants/", views.MenuItemVariantListView.as_view(), name="variant_list"),
    path("variants/create/", views.MenuItemVariantCreateView.as_view(), name="variant_create"),
    path("variants/<int:pk>/edit/", views.MenuItemVariantUpdateView.as_view(), name="variant_update"),
    path("variants/<int:pk>/delete/", views.MenuItemVariantDeleteView.as_view(), name="variant_delete"),
]
