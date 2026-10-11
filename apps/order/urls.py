from django.urls import path

from . import views

app_name = "order"

urlpatterns = [
    # سفارش‌ها
    path("", views.order_list, name="order_list"),
    path("create/", views.order_create, name="order_create"),
    path("<int:pk>/", views.order_detail, name="order_detail"),
    path("<int:pk>/edit/", views.order_update, name="order_update"),
    path("<int:pk>/delete/", views.order_delete, name="order_delete"),
    path("types/", views.order_type_list, name="order_type_list"),
    path("types/create/", views.order_type_create, name="order_type_create"),
    path("types/<int:pk>/edit/", views.order_type_update, name="order_type_update"),
    path("types/<int:pk>/delete/", views.order_type_delete, name="order_type_delete"),
]