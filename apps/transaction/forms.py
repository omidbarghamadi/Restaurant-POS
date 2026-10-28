from django import forms
from django.utils import timezone

from .models import Transaction

from apps.accounts.forms import JalaliDateTimeField, JalaliDateTimeInput

_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


class ThousandsSeparatorInput(forms.TextInput):
    """مبلغ را با جداکننده هزارگان (٬) نشان می‌دهد و در ارسال فرم آن را عدد خام می‌کند."""

    def format_value(self, value):
        if value in (None, ""):
            return value
        try:
            number = float(str(value).translate(_DIGITS).replace(",", ""))
        except (ValueError, TypeError):
            return value
        if number == int(number):
            return f"{int(number):,}"
        return f"{number:,}"

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if value:
            value = value.translate(_DIGITS).replace(",", "").strip()
        return value


class TransactionForm(forms.ModelForm):
    transaction_date = JalaliDateTimeField(
        label="تاریخ تراکنش",
        required=False,
        widget=JalaliDateTimeInput(attrs={
            "class": "form-control",
            "data-jdp": "",
            "autocomplete": "off",
            "placeholder": "۱۴۰۵/۰۱/۰۱ ۱۴:۳۰",
        }),
    )

    class Meta:
        model = Transaction

        fields = (
            "transaction_type",
            "amount",
            "payment_method",
            "employee",
            "customer",
            "description",
            "transaction_date",
        )

        widgets = {
            "transaction_type": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "amount": ThousandsSeparatorInput(
                attrs={
                    "class": "form-control amount-input",
                    "placeholder": "مبلغ را وارد کنید",
                    "inputmode": "numeric",
                    "autocomplete": "off",
                }
            ),

            "payment_method": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "employee": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "customer": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "توضیحات تراکنش",
                }
            ),
        }

        labels = {
            "transaction_type": "نوع تراکنش",
            "amount": "مبلغ",
            "payment_method": "روش پرداخت",
            "employee": "کارمند",
            "customer": "مشتری",
            "description": "توضیحات",
            "transaction_date": "تاریخ تراکنش",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # مقدار پیش‌فرض تاریخ برای تراکنش جدید
        if not self.instance.pk and not self.initial.get("transaction_date"):
            self.initial["transaction_date"] = timezone.localtime()

        # فیلدهای اختیاری
        self.fields["employee"].required = False
        self.fields["customer"].required = False
        self.fields["description"].required = False

        # مرتب‌سازی
        self.fields["employee"].queryset = (
            self.fields["employee"].queryset
            .select_related("role")
        )

        self.fields["customer"].queryset = (
            self.fields["customer"].queryset
        )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount <= 0:
            raise forms.ValidationError(
                "مبلغ تراکنش باید بیشتر از صفر باشد."
            )

        return amount

    def clean(self):
        cleaned_data = super().clean()

        transaction_type = cleaned_data.get("transaction_type")
        employee = cleaned_data.get("employee")
        customer = cleaned_data.get("customer")

        EMPLOYEE_TYPES = (
            Transaction.TransactionType.SALARY,
            Transaction.TransactionType.DELIVERY,
        )

        # پرداخت حقوق و پیک: کارمند الزامی، مشتری نامربوط
        if transaction_type in EMPLOYEE_TYPES:
            if not employee:
                self.add_error(
                    "employee",
                    "برای این نوع تراکنش، انتخاب کارمند الزامی است.",
                )
            cleaned_data["customer"] = None

        # دریافت طلب: مشتری الزامی، کارمند نامربوط
        elif transaction_type == Transaction.TransactionType.RECEIVABLE:
            if not customer:
                self.add_error(
                    "customer",
                    "برای دریافت طلب، انتخاب مشتری الزامی است.",
                )
            cleaned_data["employee"] = None

        # سایر انواع: هیچ‌کدام
        else:
            cleaned_data["employee"] = None
            cleaned_data["customer"] = None

        return cleaned_data
