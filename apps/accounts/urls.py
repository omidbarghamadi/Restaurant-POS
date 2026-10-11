from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    # =====================================================
    # Role
    # =====================================================

    path("roles/", views.RoleListView.as_view(), name="role-list",),
    path("roles/create/", views.RoleCreateView.as_view(), name="role-create",),
    path("roles/<int:pk>/edit/", views.RoleUpdateView.as_view(), name="role-update",),
    path("roles/<int:pk>/delete/", views.RoleDeleteView.as_view(), name="role-delete",),

    # =====================================================
    # Employee
    # =====================================================

    path("employees/",  views.EmployeeListView.as_view(),  name="employee-list",),
    path("employees/create/", views.EmployeeCreateView.as_view(), name="employee-create",),
    path( "employees/<int:pk>/", views.EmployeeDetailView.as_view(), name="employee-detail",),
    path("employees/<int:pk>/edit/", views.EmployeeUpdateView.as_view(), name="employee-update",),
    path("employees/<int:pk>/delete/",  views.EmployeeDeleteView.as_view(), name="employee-delete",),

    # =====================================================
    # Customer
    # =====================================================

    path("customers/", views.CustomerListView.as_view(), name="customer-list",),
    path("customers/create/", views.CustomerCreateView.as_view(), name="customer-create",),
    path("customers/<int:pk>/", views.CustomerDetailView.as_view(), name="customer-detail",),
    path("customers/<int:pk>/edit/", views.CustomerUpdateView.as_view(), name="customer-update",),
    path("customers/<int:pk>/delete/", views.CustomerDeleteView.as_view(), name="customer-delete",),
]