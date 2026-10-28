from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TransactionForm
from .models import Transaction
from django.urls import reverse
from apps.accounts.templatetags.jalali_tags import jalali, thousands_separator


def transaction_list(request):
    transactions = (
        Transaction.objects
        .select_related(
            "employee",
            "customer",
        )
        .all()
    )

    return render(
        request,
        "transaction/transaction_list.html",
        {
            "transactions": transactions,
        },
    )


def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.save()

            messages.success(
                request,
                "تراکنش با موفقیت ثبت شد.",
            )

            return redirect("transaction:transaction_list")

    else:
        form = TransactionForm()

    return render(
        request,
        "transaction/transaction_form.html",
        {
            "form": form,
        },
    )


def transaction_detail(request, pk):
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            "employee",
            "employee__role",
            "customer",
        ),
        pk=pk,
    )

    return render(
        request,
        "transaction/transaction_detail.html",
        {
            "transaction": transaction,
        },
    )


def transaction_update(request, pk):
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
    )

    if request.method == "POST":
        form = TransactionForm(
            request.POST,
            instance=transaction,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "تراکنش با موفقیت ویرایش شد.",
            )

            return redirect("transaction:transaction_list")

    else:
        form = TransactionForm(
            instance=transaction,
        )

    return render(
        request,
        "transaction/transaction_form.html",
        {
            "form": form,
            "object": transaction,
        },
    )


def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)

    if request.method == "POST":
        ...  # بدون تغییر

    return render(request, "pos/confirm_delete.html", {
        "entity_name": "تراکنش",
        "object_label": transaction.get_transaction_type_display(),
        "cancel_url": reverse("transaction:transaction_list"),
        "warning_text": "در صورت حذف، این عملیات قابل بازگشت نیست.",
        "details": [
            ("نوع تراکنش", transaction.get_transaction_type_display()),
            ("مبلغ", thousands_separator(transaction.amount)),
            ("تاریخ", jalali(transaction.transaction_date, "%Y/%m/%d %H:%M")),
        ],
    })