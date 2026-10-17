from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Category, MenuItem, MenuItemVariant
from .forms import (
    CategoryForm,
    MenuItemForm,
    MenuItemVariantForm,
)
from apps.mixins import ConfirmDeleteMixin


# ============================================================
# Category Views
# ============================================================

class CategoryListView(ListView):
    model = Category
    template_name = "menu/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.order_by("title")


class CategoryCreateView(SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("menu:category_list")
    success_message = "دسته‌بندی با موفقیت ایجاد شد."


class CategoryUpdateView(SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("menu:category_list")
    success_message = "دسته‌بندی با موفقیت ویرایش شد."


class CategoryDeleteView(ConfirmDeleteMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("menu:category_list")
    entity_name = "دسته‌بندی"
    success_message = "دسته‌بندی با موفقیت حذف شد."
    warning_text = "توجه: اگر آیتمی به این دسته‌بندی وابسته باشد، امکان حذف آن وجود ندارد."

    def get_object_label(self):
        return self.object.title


# ============================================================
# MenuItem Views
# ============================================================

class MenuItemListView(ListView):
    model = MenuItem
    template_name = "menu/menu_item_list.html"
    context_object_name = "menu_items"

    def get_queryset(self):
        queryset = (
            MenuItem.objects
            .select_related("category")
            .prefetch_related("variants")
            .order_by("category", "name")
        )

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)

        category_id = self.request.GET.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.order_by("title")
        return context


class MenuItemCreateView(SuccessMessageMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/menu_item_form.html"
    success_url = reverse_lazy("menu:menu_item_list")
    success_message = "آیتم منو با موفقیت ایجاد شد."


class MenuItemUpdateView(SuccessMessageMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/menu_item_form.html"
    success_url = reverse_lazy("menu:menu_item_list")
    success_message = "آیتم منو با موفقیت ویرایش شد."


class MenuItemDeleteView(ConfirmDeleteMixin, DeleteView):
    model = MenuItem
    success_url = reverse_lazy("menu:menu_item_list")
    entity_name = "آیتم منو"
    success_message = "آیتم منو با موفقیت حذف شد."
    warning_text = "تمام زیرمنوهای این آیتم نیز حذف خواهند شد."

    def get_object_label(self):
        return self.object.name


# ============================================================
# MenuItemVariant Views
# ============================================================

class MenuItemVariantListView(ListView):
    model = MenuItemVariant
    template_name = "menu/variant_list.html"
    context_object_name = "variants"

    def get_queryset(self):
        return (
            MenuItemVariant.objects
            .select_related("menu_item", "menu_item__category")
            .order_by("menu_item", "name")
        )


class MenuItemVariantCreateView(SuccessMessageMixin, CreateView):
    model = MenuItemVariant
    form_class = MenuItemVariantForm
    template_name = "menu/variant_form.html"
    success_url = reverse_lazy("menu:variant_list")
    success_message = "زیرمنو با موفقیت ایجاد شد."


class MenuItemVariantUpdateView(SuccessMessageMixin, UpdateView):
    model = MenuItemVariant
    form_class = MenuItemVariantForm
    template_name = "menu/variant_form.html"
    success_url = reverse_lazy("menu:variant_list")
    success_message = "زیرمنو با موفقیت ویرایش شد."


class MenuItemVariantDeleteView(ConfirmDeleteMixin, DeleteView):
    model = MenuItemVariant
    success_url = reverse_lazy("menu:variant_list")
    entity_name = "زیرمنو"
    success_message = "زیرمنو با موفقیت حذف شد."

    def get_object_label(self):
        return f"{self.object.menu_item.name} - {self.object.name}"
