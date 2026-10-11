from django import forms
from django.forms import inlineformset_factory

from .models import Order, OrderItem, OrderType
from apps.accounts.models import Customer, Employee
from apps.menu.models import MenuItemVariant


class VariantSelect(forms.Select):
    """
    ویجت اختصاصی برای انتخاب زیرمنو (واریانت محصول).

    قیمت هر زیرمنو را به صورت attribute (data-price) روی <option>
    خروجی می‌دهد تا در سمت کلاینت بتوان بدون درخواست جداگانه،
    جمع کل سفارش را به صورت زنده محاسبه کرد.
    """

    def __init__(self, *args, prices=None, **kwargs):
        self.prices = prices or {}
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )

        raw_value = value.value if hasattr(value, "value") else value

        if raw_value not in (None, ""):
            price = self.prices.get(int(raw_value))

            if price is not None:
                option["attrs"]["data-price"] = price

        return option


class OrderTypeForm(forms.ModelForm):
    """
    فرم ایجاد و ویرایش نوع سفارش
    """

    class Meta:
        model = OrderType
        fields = (
            "name",
            "is_active",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "مثلاً حضوری - داخل سالن",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class OrderForm(forms.ModelForm):
    """
    فرم اصلی ثبت سفارش در POS
    """

    class Meta:
        model = Order

        fields = (
            "customer",
            "employee",
            "order_type",
            "table_number",
            "description",
            "discount",
            "delivery",
            "packaging_cost",
            "payment_method",
            "order_date",
            "order_time",
        )

        widgets = {
            # تاریخ میلادی؛ کاربر تاریخ شمسی را در قالب می‌بیند و
            # جاوااسکریپت مقدار این فیلد مخفی را پر می‌کند.
            "order_date": forms.HiddenInput(),

            # ساعت با تقویم‌ک شمسی (فقط زمان) انتخاب می‌شود
            "order_time": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "class": "form-control",
                    "placeholder": "انتخاب ساعت",
                    "autocomplete": "off",
                    "data-jdp": True,
                    "data-jdp-only-time": True,
                    "data-jdp-has-second": "false",
                },
            ),

            "customer": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "employee": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "order_type": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "table_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "شماره میز",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "توضیحات سفارش",
                }
            ),

            "discount": forms.TextInput(
                attrs={
                    "class": "form-control money-input",
                    "inputmode": "numeric",
                    "placeholder": "مبلغ تخفیف",
                }
            ),

            "delivery": forms.TextInput(
                attrs={
                    "class": "form-control money-input",
                    "inputmode": "numeric",
                    "placeholder": "هزینه پیک",
                }
            ),

            "packaging_cost": forms.TextInput(
                attrs={
                    "class": "form-control money-input",
                    "inputmode": "numeric",
                    "placeholder": "هزینه بسته‌بندی",
                }
            ),

            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # فقط مشتریان موجود در لیست نمایش داده شوند
        self.fields["customer"].queryset = Customer.objects.all()

        # فقط کارمندان موجود نمایش داده شوند
        self.fields["employee"].queryset = Employee.objects.all()

        # فقط نوع‌های سفارش فعال نمایش داده شوند
        self.fields["order_type"].queryset = OrderType.objects.filter(
            is_active=True
        )

        # انتخاب مشتری اختیاری است
        self.fields["customer"].required = False

        # انتخاب کارمند اختیاری است
        self.fields["employee"].required = False

        # شماره میز اختیاری است
        self.fields["table_number"].required = False

        # توضیحات اختیاری است
        self.fields["description"].required = False

        # نوع پرداخت در شروع سفارش می‌تواند خالی باشد
        self.fields["payment_method"].required = False

    def clean(self):
        cleaned_data = super().clean()

        order_type = cleaned_data.get("order_type")
        table_number = cleaned_data.get("table_number")
        payment_method = cleaned_data.get("payment_method")

        # --------------------------------------------------
        # بررسی شماره میز
        # --------------------------------------------------

        if (
                cleaned_data.get("payment_method") == Order.PaymentMethod.CREDIT
                and not cleaned_data.get("customer")
        ):
            self.add_error("customer", "برای سفارش نسیه انتخاب مشتری الزامی است.")

        if order_type:
            order_type_name = order_type.name.strip()

            # اگر سفارش داخل سالن باشد، شماره میز الزامی است
            if "داخل سالن" in order_type_name:
                if not table_number:
                    self.add_error(
                        "table_number",
                        "برای سفارش داخل سالن، شماره میز الزامی است."
                    )

            # برای سایر انواع سفارش شماره میز لازم نیست
            else:
                cleaned_data["table_number"] = None

        return cleaned_data


class OrderItemForm(forms.ModelForm):
    """
    فرم هر آیتم سفارش

    قیمت واحد و مبلغ کل از سمت کاربر دریافت نمی‌شوند.
    این مقادیر باید در سمت سرور از MenuItemVariant محاسبه شوند.
    """

    class Meta:
        model = OrderItem

        fields = (
            "variant",
            "quantity",
            "note",
        )

        widgets = {
            "variant": VariantSelect(
                attrs={
                    "class": "form-control menu-item-select",
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control quantity-input",
                    "min": 1,
                    "value": 1,
                }
            ),

            "note": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "توضیحات آیتم",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # فقط زیرمنوهایی که خودشان و آیتم منوی والدشان قابل‌فروش هستند
        variants = MenuItemVariant.objects.filter(
            is_available=True,
            menu_item__is_available=True,
            menu_item__category__is_active=True,
        ).select_related("menu_item", "menu_item__category")

        self.fields["variant"].queryset = variants

        # انتخاب زیرمنو الزامی است چون قیمت سفارش از همینجا خوانده می‌شود
        self.fields["variant"].required = True

        # قیمت هر زیرمنو برای محاسبه زنده جمع کل در سمت کلاینت
        self.fields["variant"].widget.prices = dict(
            variants.values_list("id", "price")
        )

        self.fields["note"].required = False

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")

        if quantity is not None and quantity < 1:
            raise forms.ValidationError(
                "تعداد باید حداقل ۱ باشد."
            )

        return quantity


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)

# در ویرایش نباید ردیف خالی اضافه نمایش داده شود
OrderItemEditFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=0,
    can_delete=True,
)