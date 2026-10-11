from django import forms

from .models import Customer, Employee, Role
import re
import jdatetime
from datetime import date, datetime
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = [
            "title",
            "description",
        ]

        labels = {
            "title": "عنوان نقش",
            "description": "توضیحات",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "مثلاً صندوق‌دار",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "توضیحات مربوط به نقش",
                    "rows": 3,
                }
            ),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if not title:
            raise forms.ValidationError(
                "عنوان نقش نمی‌تواند خالی باشد."
            )

        return title

_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


class MoneyWidget(forms.TextInput):
    """مبلغ را با جداکننده سه‌رقمی و راست‌به‌چپ صحیح (LTR) نمایش می‌دهد."""

    def format_value(self, value):
        if value in (None, ""):
            return value
        try:
            return "{:,}".format(int(value))
        except (ValueError, TypeError):
            return value


class MoneyField(forms.IntegerField):
    """ورودی مبلغ را از جداکننده هزارگان و اعداد فارسی پاک‌سازی می‌کند."""

    widget = MoneyWidget

    def to_python(self, value):
        if value in self.empty_values:
            return None
        value = str(value).strip().translate(_DIGITS)
        value = value.replace(",", "").replace("،", "")
        return super().to_python(value)


class JalaliDateInput(forms.TextInput):
    """مقدار میلادی دیتابیس را به شمسی نشان می‌دهد."""

    def format_value(self, value):
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, date):
            return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")
        return value


class JalaliDateField(forms.DateField):
    """ورودی شمسی (۱۴۰۵/۰۷/۰۲) را به date میلادی تبدیل می‌کند."""

    widget = JalaliDateInput

    def to_python(self, value):
        if value in self.empty_values:
            return None
        value = str(value).strip().translate(_DIGITS)
        try:
            y, m, d = map(int, re.split(r"[/\-]", value))
            return jdatetime.date(y, m, d).togregorian()
        except (ValueError, TypeError):
            raise ValidationError("تاریخ وارد شده معتبر نیست.", code="invalid")


class JalaliDateTimeInput(forms.TextInput):
    """مقدار میلادی دیتابیس را به تاریخ و زمان شمسی نشان می‌دهد."""

    def format_value(self, value):
        if isinstance(value, str) or value is None:
            return value
        if isinstance(value, datetime):
            if timezone.is_aware(value):
                value = timezone.localtime(value)
            return jdatetime.datetime.fromgregorian(datetime=value).strftime(
                "%Y/%m/%d %H:%M"
            )
        if isinstance(value, date):
            return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")
        return value


class JalaliDateTimeField(forms.DateTimeField):
    """ورودی تاریخ و زمان شمسی (۱۴۰۵/۰۷/۰۲ ۱۴:۳۰) را به datetime میلادی تبدیل می‌کند."""

    widget = JalaliDateTimeInput

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, datetime):
            return value

        value = str(value).strip().translate(_DIGITS)

        try:
            if " " in value:
                date_part, time_part = value.split(" ", 1)
            else:
                date_part, time_part = value, "00:00"

            y, m, d = map(int, re.split(r"[/\-]", date_part))
            time_bits = [int(bit) for bit in re.split(r"[:.]", time_part) if bit]
            h = time_bits[0] if len(time_bits) > 0 else 0
            mi = time_bits[1] if len(time_bits) > 1 else 0
            se = time_bits[2] if len(time_bits) > 2 else 0

            gregorian_dt = jdatetime.datetime(y, m, d, h, mi, se).togregorian()

            if settings.USE_TZ and timezone.is_naive(gregorian_dt):
                gregorian_dt = timezone.make_aware(gregorian_dt)

            return gregorian_dt
        except (ValueError, TypeError):
            raise ValidationError(
                "تاریخ و زمان وارد شده معتبر نیست.", code="invalid"
            )


class EmployeeForm(forms.ModelForm):
    hire_date = JalaliDateField(
        label="تاریخ استخدام",
        required=False,
        widget=JalaliDateInput(attrs={
            "class": "form-control",
            "data-jdp": "",
            "autocomplete": "off",
            "placeholder": "۱۴۰۵/۰۱/۰۱",
        }),
    )

    balance = MoneyField(
        label="جمع دریافتی",
        initial=0,
        widget=MoneyWidget(attrs={
            "class": "form-control",
            "dir": "ltr",
            "inputmode": "numeric",
            "placeholder": "0",
        }),
    )

    class Meta:
        model = Employee

        fields = [
            "role",
            "first_name",
            "last_name",
            "mobile",
            "national_code",
            "address",
            "hire_date",
            "balance",
            "status",
            "description",
        ]

        labels = {
            "role": "نقش",
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "mobile": "موبایل",
            "national_code": "کد ملی",
            "address": "آدرس",
            "hire_date": "تاریخ استخدام",
            "balance": "جمع دریافتی",
            "status": "وضعیت",
            "description": "توضیحات",
        }

        widgets = {
            "role": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام خانوادگی",
                }
            ),
            "mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "09123456789",
                    "maxlength": "11",
                    "inputmode": "numeric",
                }
            ),
            "national_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "کد ملی",
                    "maxlength": "10",
                    "inputmode": "numeric",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "آدرس",
                    "rows": 3,
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "توضیحات",
                    "rows": 3,
                }
            ),
        }

    def clean_balance(self):
        balance = self.cleaned_data.get("balance")

        if balance is None:
            return balance

        if balance < 0:
            raise forms.ValidationError(
                "جمع دریافتی نمی‌تواند عددی منفی باشد."
            )

        return balance

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"].strip()

        if not first_name:
            raise forms.ValidationError(
                "نام نمی‌تواند خالی باشد."
            )

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"].strip()

        if not last_name:
            raise forms.ValidationError(
                "نام خانوادگی نمی‌تواند خالی باشد."
            )

        return last_name

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"].strip()

        if not mobile.isdigit():
            raise forms.ValidationError(
                "شماره موبایل باید فقط شامل اعداد باشد."
            )

        if len(mobile) != 11 or not mobile.startswith("09"):
            raise forms.ValidationError(
                "شماره موبایل باید به صورت 09123456789 وارد شود."
            )

        return mobile

    def clean_national_code(self):
        national_code = self.cleaned_data.get("national_code")

        if not national_code:
            return national_code

        national_code = national_code.strip()

        if not national_code.isdigit():
            raise forms.ValidationError(
                "کد ملی باید فقط شامل اعداد باشد."
            )

        if len(national_code) != 10:
            raise forms.ValidationError(
                "کد ملی باید ۱۰ رقم باشد."
            )

        return national_code


class CustomerForm(forms.ModelForm):
    balance = MoneyField(
        label="مانده حساب",
        initial=0,
        widget=MoneyWidget(attrs={
            "class": "form-control",
            "dir": "ltr",
            "inputmode": "numeric",
            "placeholder": "0",
        }),
    )

    class Meta:
        model = Customer

        fields = [
            "subscription_code",
            "name",
            "mobile",
            "phone",
            "address",
            "balance",
            "description",
        ]

        labels = {
            "subscription_code": "کد اشتراک",
            "name": "نام مشتری",
            "mobile": "موبایل",
            "phone": "تلفن",
            "address": "آدرس",
            "balance": "مانده حساب",
            "description": "توضیحات",
        }

        widgets = {
            "subscription_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "مثلاً 1001",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام و نام خانوادگی",
                }
            ),
            "mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "09123456789",
                    "maxlength": "11",
                    "inputmode": "numeric",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "02112345678",
                    "maxlength": "11",
                    "inputmode": "numeric",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "آدرس مشتری",
                    "rows": 3,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "توضیحات",
                    "rows": 3,
                }
            ),
        }

    def clean_subscription_code(self):
        subscription_code = (
            self.cleaned_data["subscription_code"].strip()
        )

        if not subscription_code:
            raise forms.ValidationError(
                "کد اشتراک نمی‌تواند خالی باشد."
            )

        return subscription_code

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError(
                "نام مشتری نمی‌تواند خالی باشد."
            )

        return name

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"].strip()

        if not mobile.isdigit():
            raise forms.ValidationError(
                "شماره موبایل باید فقط شامل اعداد باشد."
            )

        if len(mobile) != 11 or not mobile.startswith("09"):
            raise forms.ValidationError(
                "شماره موبایل باید به صورت 09123456789 وارد شود."
            )

        return mobile

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone:
            return phone

        phone = phone.strip()

        if not phone.isdigit():
            raise forms.ValidationError(
                "شماره تلفن باید فقط شامل اعداد باشد."
            )

        return phone
