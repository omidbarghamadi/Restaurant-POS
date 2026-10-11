"""
سیگنال‌هایی که بعد از هر تغییر در Transaction (ثبت، ویرایش، حذف)،
فیلد balance مربوط به Employee و Customor رو به‌روز نگه می‌دارن.

منطق:
- کارمند: هر تراکنشی که "employee" داشته باشه، amount به balance کارمند
  (جمع دریافتی) اضافه می‌شه.
- مشتری: فقط تراکنش نوع "دریافت طلب" (receivable) که "customer" داشته
  باشه، amount از balance مشتری (مانده حساب) کم می‌شه.
- ویرایش: اثر نسخه‌ی قبلی تراکنش خنثی و اثر نسخه‌ی جدید اعمال می‌شه.
- حذف: اثر تراکنش خنثی می‌شه.

نکته: از .update() با F() استفاده شده تا آپدیت balance در سطح دیتابیس و
به‌صورت اتمیک انجام بشه (بدون race condition و بدون فراخوانی .save()
روی Employee/Customer که ممکنه سیگنال‌های دیگه‌ای رو تریگر کنه).
"""

from django.db import transaction as db_transaction
from django.db.models import F
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import Transaction
from apps.accounts.models import Employee, Customer


def _employee_effect(employee_id, amount):
    """اثر یک تراکنش روی balance کارمند (جمع دریافتی)."""
    if employee_id and amount:
        return amount
    return 0


def _customer_effect(customer_id, transaction_type, amount):
    """اثر یک تراکنش روی balance مشتری (مانده حساب) - فقط دریافت طلب."""
    if customer_id and amount and transaction_type == Transaction.TransactionType.RECEIVABLE:
        return +amount
    return 0


def _apply_employee_delta(employee_id, delta):
    if employee_id and delta:
        Employee.objects.filter(pk=employee_id).update(
            balance=F("balance") + delta
        )


def _apply_customer_delta(customer_id, delta):
    if customer_id and delta:
        Customer.objects.filter(pk=customer_id).update(
            balance=F("balance") + delta
        )


@receiver(pre_save, sender=Transaction)
def stash_old_transaction(sender, instance, **kwargs):
    """
    قبل از ذخیره، نسخه‌ی قبلیِ تراکنش (در صورت ویرایش) رو از دیتابیس
    می‌خونیم تا بعداً بشه اثر قدیمیش رو خنثی کرد.
    """
    if instance.pk:
        instance._old_transaction = (
            Transaction.objects
            .filter(pk=instance.pk)
            .only("employee_id", "customer_id", "amount", "transaction_type")
            .first()
        )
    else:
        instance._old_transaction = None


@receiver(post_save, sender=Transaction)
def sync_balances_on_save(sender, instance, created, **kwargs):
    old = getattr(instance, "_old_transaction", None)

    with db_transaction.atomic():
        # خنثی کردن اثر نسخه‌ی قبلی تراکنش (اگه ویرایش بوده)
        if old is not None:
            _apply_employee_delta(
                old.employee_id,
                -_employee_effect(old.employee_id, old.amount),
            )
            _apply_customer_delta(
                old.customer_id,
                -_customer_effect(old.customer_id, old.transaction_type, old.amount),
            )

        # اعمال اثر نسخه‌ی فعلی تراکنش
        _apply_employee_delta(
            instance.employee_id,
            _employee_effect(instance.employee_id, instance.amount),
        )
        _apply_customer_delta(
            instance.customer_id,
            _customer_effect(instance.customer_id, instance.transaction_type, instance.amount),
        )

    if hasattr(instance, "_old_transaction"):
        del instance._old_transaction


@receiver(post_delete, sender=Transaction)
def reverse_balances_on_delete(sender, instance, **kwargs):
    """موقع حذف تراکنش، اثری که قبلاً روی balance گذاشته بود خنثی می‌شه."""
    with db_transaction.atomic():
        _apply_employee_delta(
            instance.employee_id,
            -_employee_effect(instance.employee_id, instance.amount),
        )
        _apply_customer_delta(
            instance.customer_id,
            -_customer_effect(instance.customer_id, instance.transaction_type, instance.amount),
        )