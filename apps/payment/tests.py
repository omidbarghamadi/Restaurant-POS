from django.test import TestCase

from apps.order.models import Order, OrderType
from apps.payment.models import Payment


class PaymentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.order_type = OrderType.objects.create(
            name="حضوری",
        )

        cls.order = Order.objects.create(
            order_number=100,
            order_type=cls.order_type,
        )

        cls.payment = Payment.objects.create(
            order=cls.order,
            method=Payment.PaymentMethod.CASH,
            amount=250000,
            note="پرداخت نقدی",
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(
            self.payment.method,
            Payment.PaymentMethod.CASH,
        )
        self.assertEqual(self.payment.amount, 250000)
        self.assertEqual(self.payment.note, "پرداخت نقدی")

    def test_payment_default_method(self):
        payment = Payment.objects.create(
            order=self.order,
            amount=100000,
        )

        self.assertEqual(
            payment.method,
            Payment.PaymentMethod.UNKNOWN,
        )

    def test_payment_str(self):
        expected = (
            f"{self.order} - "
            f"{self.payment.amount} - "
            f"{self.payment.get_method_display()}"
        )

        self.assertEqual(
            str(self.payment),
            expected,
        )

    def test_payment_date_is_created_automatically(self):
        self.assertIsNotNone(self.payment.payment_date)

    def test_payment_methods(self):
        methods = [
            Payment.PaymentMethod.CASH,
            Payment.PaymentMethod.CARD,
            Payment.PaymentMethod.CARD_TO_CARD,
            Payment.PaymentMethod.CREDIT,
            Payment.PaymentMethod.FREE,
            Payment.PaymentMethod.STAFF_MEAL,
            Payment.PaymentMethod.UNKNOWN,
        ]

        for method in methods:
            payment = Payment.objects.create(
                order=self.order,
                method=method,
                amount=100000,
            )

            self.assertEqual(payment.method, method)

    def test_payment_note_is_optional(self):
        payment = Payment.objects.create(
            order=self.order,
            method=Payment.PaymentMethod.CARD,
            amount=300000,
        )

        self.assertEqual(payment.note, "")