from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
)

from .models import Role, Employee, Customer
from .forms import RoleForm, EmployeeForm, CustomerForm
from django.db.models import Sum
from apps.order.models import Order

# =========================================================
# Role Views
# =========================================================


class RoleListView(ListView):
    model = Role
    template_name = "role-list.html"
    context_object_name = "roles"


class RoleCreateView(CreateView):
    model = Role
    form_class = RoleForm
    template_name = "role-form.html"
    success_url = reverse_lazy("accounts:role-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "نقش با موفقیت ایجاد شد."
        )
        return super().form_valid(form)


class RoleUpdateView(UpdateView):
    model = Role
    form_class = RoleForm
    template_name = "role-form.html"
    success_url = reverse_lazy("accounts:role-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "نقش با موفقیت ویرایش شد."
        )
        return super().form_valid(form)


class RoleDeleteView(DeleteView):
    model = Role
    template_name = "role-confirm_delete.html"
    success_url = reverse_lazy("accounts:role-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "نقش با موفقیت حذف شد."
        )
        return super().form_valid(form)


# =========================================================
# Employee Views
# =========================================================

class EmployeeListView(ListView):
    model = Employee
    template_name = "employee-list.html"
    context_object_name = "employees"


class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employee-form.html"
    success_url = reverse_lazy("accounts:employee-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "کارمند با موفقیت ایجاد شد."
        )
        return super().form_valid(form)


class EmployeeDetailView(DetailView):
    model = Employee
    template_name = "employee-detail.html"
    context_object_name = "employee"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = self.object.transactions.all()  # مرتب‌سازی از Meta: جدیدترین اول
        context["transactions"] = transactions
        context["transactions_total"] = (
                transactions.aggregate(total=Sum("amount"))["total"] or 0
        )
        return context


class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employee-form.html"
    success_url = reverse_lazy("accounts:employee-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "اطلاعات کارمند با موفقیت ویرایش شد."
        )
        return super().form_valid(form)


class EmployeeDeleteView(DeleteView):
    model = Employee
    template_name = "employee-confirm_delete.html"
    success_url = reverse_lazy("accounts:employee-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "کارمند با موفقیت حذف شد."
        )
        return super().form_valid(form)


# =========================================================
# Customer Views
# =========================================================

class CustomerListView(ListView):
    model = Customer
    template_name = "customer-list.html"
    context_object_name = "customers"

    def get_queryset(self):
        return Customer.objects.all().order_by("balance")


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customer-form.html"
    success_url = reverse_lazy("accounts:customer-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "مشتری با موفقیت ایجاد شد."
        )
        return super().form_valid(form)


class CustomerDetailView(DetailView):
    model = Customer
    template_name = "customer-detail.html"
    context_object_name = "customer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object

        context["transactions"] = customer.transactions.all()  # ترتیب: جدیدترین اول

        credit_orders = (
            customer.orders
            .filter(payment_method=Order.PaymentMethod.CREDIT)
            .select_related("order_type")
            .order_by("-order_date", "-order_time")
        )
        context["credit_orders"] = credit_orders
        context["credit_total"] = credit_orders.aggregate(
            total=Sum("total_price")
        )["total"] or 0

        return context


class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customer-form.html"
    success_url = reverse_lazy("accounts:customer-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "اطلاعات مشتری با موفقیت ویرایش شد."
        )
        return super().form_valid(form)


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = "customer-confirm_delete.html"
    success_url = reverse_lazy("accounts:customer-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "مشتری با موفقیت حذف شد."
        )
        return super().form_valid(form)
