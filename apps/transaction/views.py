from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TransactionForm
from .models import Transaction


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
        "transactions/transaction_list.html",
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
        "transactions/transaction_form.html",
        {
            "form": form,
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
        "transactions/transaction_form.html",
        {
            "form": form,
            "object": transaction,
        },
    )


def transaction_delete(request, pk):
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
    )

    if request.method == "POST":
        transaction.delete()

        messages.success(
            request,
            "تراکنش با موفقیت حذف شد.",
        )

        return redirect("transaction:transaction_list")

    return render(
        request,
        "transactions/transaction_confirm_delete.html",
        {
            "transaction": transaction,
        },
    )