from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Customer, Employee, Role
from .models import Transaction


User = get_user_model()


class TransactionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="testpass123",
        )

        self.role = Role.objects.create(
            title="صندوق دار",
        )

        self.employee = Employee.objects.create(
            user=self.user,
            role=self.role,
        )

        self.customer = Customer.objects.create(
            name="مشتری تست",
        )

    def test_create_transaction(self):
        transaction = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.SALARY,
            amount=10_000_000,
            payment_method=Transaction.PaymentMethod.CASH,
            employee=self.employee,
            description="پرداخت حقوق",
            transaction_date="2026-08-22 12:00:00",
            paid_by=self.user,
        )

        self.assertEqual(transaction.amount, 10_000_000)
        self.assertEqual(
            transaction.transaction_type,
            Transaction.TransactionType.SALARY,
        )
        self.assertEqual(
            transaction.payment_method,
            Transaction.PaymentMethod.CASH,
        )

    def test_transaction_str(self):
        transaction = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.REPAIR,
            amount=500_000,
            transaction_date="2026-08-22 12:00:00",
            paid_by=self.user,
        )

        self.assertEqual(
            str(transaction),
            "تعمیرات - 500000",
        )

    def test_transaction_with_employee(self):
        transaction = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.SALARY,
            amount=15_000_000,
            employee=self.employee,
            transaction_date="2026-08-22 12:00:00",
            paid_by=self.user,
        )

        self.assertEqual(transaction.employee, self.employee)

    def test_transaction_with_customer(self):
        transaction = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.RECEIVABLE,
            amount=2_000_000,
            customer=self.customer,
            transaction_date="2026-08-22 12:00:00",
            paid_by=self.user,
        )

        self.assertEqual(transaction.customer, self.customer)

    def test_paid_by(self):
        transaction = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.EXPENSE,
            amount=300_000,
            transaction_date="2026-08-22 12:00:00",
            paid_by=self.user,
        )

        self.assertEqual(transaction.paid_by, self.user)
        self.assertIn(
            transaction,
            self.user.paid_transactions.all(),
        )

    def test_payment_method_choices(self):
        transaction = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.RAW_MATERIAL,
            amount=1_000_000,
            payment_method=Transaction.PaymentMethod.CARD_TO_CARD,
            transaction_date="2026-08-22 12:00:00",
            paid_by=self.user,
        )

        self.assertEqual(
            transaction.get_payment_method_display(),
            "کارت به کارت",
        )

    def test_optional_fields_can_be_empty(self):
        transaction = Transaction.objects.create(
            transaction_type=Transaction.TransactionType.OTHER_EXPENSE,
            amount=100_000,
            transaction_date="2026-08-22 12:00:00",
            paid_by=self.user,
        )

        self.assertIsNone(transaction.employee)
        self.assertIsNone(transaction.customer)
        self.assertEqual(transaction.description, "")