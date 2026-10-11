from datetime import date, datetime

import jdatetime
from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def jalali(value, fmt="%Y/%m/%d"):
    """تاریخ (و در صورت وجود، ساعت) میلادی را به شمسی تبدیل می‌کند. مثال: {{ obj.date|jalali }}"""
    if not value:
        return ""

    if isinstance(value, datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return jdatetime.datetime.fromgregorian(datetime=value).strftime(fmt)

    if isinstance(value, date):
        return jdatetime.date.fromgregorian(date=value).strftime(fmt)

    return value


@register.filter
def thousands_separator(value):
    """عدد را با جداکننده هزارگان نشان می‌دهد. مثال: {{ transaction.amount|thousands_separator }}"""
    if value in (None, ""):
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    if number == int(number):
        return f"{int(number):,}"
    return f"{number:,}"