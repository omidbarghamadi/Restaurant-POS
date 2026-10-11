from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    OrderForm,
    OrderItemEditFormSet,
    OrderItemFormSet,
    OrderTypeForm,
)
from .models import Order, OrderItem, OrderType
from .services import get_next_order_number

from apps.accounts.models import Customer


def adjust_customer_balance(customer_id, payment_method, total_price, reverse=False):
    """
    اگر سفارش نسیه باشد، مبلغ کل از بالانس مشتری کم می‌شود (منفی‌تر).
    با reverse=True همین مبلغ به بالانس برمی‌گردد (برای ویرایش/حذف).
    """
    if payment_method != Order.PaymentMethod.CREDIT or not customer_id:
        return

    delta = total_price if reverse else -total_price

    Customer.objects.filter(pk=customer_id).update(
        balance=F("balance") + delta
    )


def get_customers_data():
    """
    اطلاعات مشتری‌ها به‌صورت دیکشنری {id: {...}} برای نمایش آنی
    در فرم سفارش (بدون درخواست اضافه به سرور).
    """

    return {
        str(c["pk"]): {
            "code": c["subscription_code"],
            "name": c["name"],
            "mobile": c["mobile"],
            "phone": c["phone"] or "",
            "address": c["address"] or "",
            "balance": c["balance"],
        }
        for c in Customer.objects.values(
            "pk",
            "subscription_code",
            "name",
            "mobile",
            "phone",
            "address",
            "balance",
        )
    }


def order_list(request):
    """
    نمایش لیست سفارش‌ها
    """

    orders = (
        Order.objects
        .select_related(
            "customer",
            "employee",
            "order_type",
        )
        .prefetch_related("items__menu_item", "items__variant")
        .all()
    )

    context = {
        "orders": orders,
    }

    return render(
        request,
        "order-list.html",
        context,
    )


def order_create(request):
    """
    ثبت سفارش جدید
    """

    if request.method == "POST":
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and item_formset.is_valid():

            with transaction.atomic():

                # ایجاد سفارش
                order = order_form.save(commit=False)

                # تولید شماره سفارش
                order.order_number = get_next_order_number()

                # تاریخ سفارش توسط مدل تعیین می‌شود
                order.save()

                # اتصال آیتم‌ها به سفارش
                items = item_formset.save(commit=False)

                total_items_price = 0

                for item in items:

                    # آیتم منو و قیمت واقعی از زیرمنوی انتخاب‌شده گرفته می‌شود
                    item.menu_item = item.variant.menu_item
                    item.unit_price = item.variant.price

                    # محاسبه مبلغ آیتم
                    item.total_price = (
                        item.unit_price * item.quantity
                    )

                    item.order = order
                    item.save()

                    total_items_price += item.total_price

                # حذف آیتم‌هایی که کاربر مشخص کرده است
                for item in item_formset.deleted_objects:
                    item.delete()

                # محاسبه مبلغ نهایی سفارش
                order.total_price = (
                    total_items_price
                    + order.delivery
                    + order.packaging_cost
                    - order.discount
                )

                # جلوگیری از منفی شدن مبلغ سفارش
                if order.total_price < 0:
                    order.total_price = 0

                order.save(
                    update_fields=[
                        "total_price",
                        "updated_at",
                    ]
                )

                adjust_customer_balance(
                    order.customer_id,
                    order.payment_method,
                    order.total_price,
                )

            messages.success(
                request,
                f"سفارش شماره {order.order_number} با موفقیت ثبت شد."
            )

            return redirect(
                "order:order_detail",
                pk=order.pk,
            )

    else:
        order_form = OrderForm()
        item_formset = OrderItemFormSet()

    context = {
        "order_form": order_form,
        "item_formset": item_formset,
        "customers_data": get_customers_data(),
    }

    return render(
        request,
        "order-form.html",
        context,
    )


def order_detail(request, pk):
    """
    نمایش جزئیات یک سفارش
    """

    order = get_object_or_404(
        Order.objects
        .select_related(
            "customer",
            "employee",
            "order_type",
        )
        .prefetch_related("items__menu_item", "items__variant"),
        pk=pk,
    )

    context = {
        "order": order,
    }

    return render(
        request,
        "order-detail.html",
        context,
    )


def order_update(request, pk):
    """
    ویرایش سفارش
    """

    order = get_object_or_404(
        Order.objects.prefetch_related("items__menu_item", "items__variant"),
        pk=pk,
    )

    if request.method == "POST":
        order_form = OrderForm(
            request.POST,
            instance=order,
        )

        item_formset = OrderItemEditFormSet(
            request.POST,
            instance=order,
        )

        if order_form.is_valid() and item_formset.is_valid():

            with transaction.atomic():

                old = (
                    Order.objects
                    .select_for_update()
                    .values("customer_id", "payment_method", "total_price")
                    .get(pk=order.pk)
                )

                order = order_form.save(commit=False)

                # قیمت و زیرمنوی ذخیره‌شده‌ی آیتم‌ها در دیتابیس (قبل از هر تغییر).
                # از کوئری تازه استفاده می‌شود چون نمونه‌های formset در
                # is_valid() با داده‌ی فرم به‌روز شده‌اند.
                saved_items = {
                    row["pk"]: row
                    for row in OrderItem.objects
                    .filter(order=order)
                    .values("pk", "variant_id", "unit_price")
                }

                items = item_formset.save(commit=False)

                for item in items:

                    item.menu_item = item.variant.menu_item

                    # آیتم قبلی با همان زیرمنو: قیمت زمان ثبت سفارش حفظ می‌شود
                    # (تغییر قیمت زیرمنو نباید سفارش‌های قدیمی را عوض کند).
                    # آیتم جدید یا آیتمی که زیرمنویش عوض شده، قیمت فعلی را می‌گیرد.
                    saved = saved_items.get(item.pk)

                    if saved and saved["variant_id"] == item.variant_id:
                        item.unit_price = saved["unit_price"]
                    else:
                        item.unit_price = item.variant.price

                    item.total_price = (
                        item.unit_price * item.quantity
                    )

                    item.order = order
                    item.save()

                for item in item_formset.deleted_objects:
                    item.delete()

                # formset.save(commit=False) فقط آیتم‌های جدید/تغییرکرده را
                # برمی‌گرداند؛ پس جمع اقلام باید از کل آیتم‌های سفارش در
                # دیتابیس محاسبه شود، نه فقط از همان‌ها.
                total_items_price = (
                    order.items.aggregate(total=Sum("total_price"))["total"] or 0
                )

                order.total_price = (
                    total_items_price
                    + order.delivery
                    + order.packaging_cost
                    - order.discount
                )

                if order.total_price < 0:
                    order.total_price = 0

                order.save()

                # برگرداندن اثر قبلی و اعمال اثر جدید
                adjust_customer_balance(
                    old["customer_id"],
                    old["payment_method"],
                    old["total_price"],
                    reverse=True,
                )
                adjust_customer_balance(
                    order.customer_id,
                    order.payment_method,
                    order.total_price,
                )

            messages.success(
                request,
                f"سفارش شماره {order.order_number} با موفقیت ویرایش شد."
            )

            return redirect(
                "order:order_detail",
                pk=order.pk,
            )

    else:
        order_form = OrderForm(instance=order)
        item_formset = OrderItemEditFormSet(instance=order)

    context = {
        "order": order,
        "order_form": order_form,
        "item_formset": item_formset,
        "customers_data": get_customers_data(),
    }

    return render(
        request,
        "order-form.html",
        context,
    )


def order_delete(request, pk):
    """
    حذف سفارش
    """

    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        order_number = order.order_number

        with transaction.atomic():
            adjust_customer_balance(
                order.customer_id,
                order.payment_method,
                order.total_price,
                reverse=True,
            )
            order.delete()

        messages.success(
            request,
            f"سفارش شماره {order_number} حذف شد."
        )

        return redirect("order:order_list")

    return render(
        request,
        "order-confirm_delete.html",
        {
            "order": order,
        },
    )


def order_type_list(request):
    """
    نمایش انواع سفارش
    """

    order_types = OrderType.objects.all()

    return render(
        request,
        "order-type_list.html",
        {
            "order_types": order_types,
        },
    )


def order_type_create(request):
    """
    ایجاد نوع سفارش
    """

    if request.method == "POST":
        form = OrderTypeForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "نوع سفارش با موفقیت ایجاد شد."
            )

            return redirect("order:order_type_list")

    else:
        form = OrderTypeForm()

    return render(
        request,
        "order-type_form.html",
        {
            "form": form,
        },
    )


def order_type_update(request, pk):
    """
    ویرایش نوع سفارش
    """

    order_type = get_object_or_404(
        OrderType,
        pk=pk,
    )

    if request.method == "POST":
        form = OrderTypeForm(
            request.POST,
            instance=order_type,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "نوع سفارش با موفقیت ویرایش شد."
            )

            return redirect("order:order_type_list")

    else:
        form = OrderTypeForm(
            instance=order_type,
        )

    return render(
        request,
        "order-type_form.html",
        {
            "form": form,
            "order_type": order_type,
        },
    )


def order_type_delete(request, pk):
    """
    حذف نوع سفارش
    """

    order_type = get_object_or_404(
        OrderType,
        pk=pk,
    )

    if request.method == "POST":

        order_type.delete()

        messages.success(
            request,
            "نوع سفارش با موفقیت حذف شد."
        )

        return redirect("order:order_type_list")

    return render(
        request,
        "order-type_confirm_delete.html",
        {
            "order_type": order_type,
        },
    )