from django import forms

from .models import Category, MenuItem, MenuItemVariant


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = (
            "title",
            "is_active",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام دسته را وارد کنید",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = (
            "name",
            "category",
            "is_available",
            "image",
            "description",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام آیتم منو را وارد کنید",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "is_available": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "توضیحات آیتم را وارد کنید",
                }
            ),
        }


class MenuItemVariantForm(forms.ModelForm):
    class Meta:
        model = MenuItemVariant
        fields = (
            "menu_item",
            "name",
            "price",
            "is_available",
        )

        widgets = {
            "menu_item": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "مثلاً قارچ و پنیر",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "قیمت را وارد کنید",
                    "min": 0,
                }
            ),
            "is_available": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
