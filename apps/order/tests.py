from datetime import date
from apps.order.services import get_next_order_number
from django.test import TestCase
from django.db import IntegrityError

from apps.menu.models import Category, MenuItem
from apps.order.models import (
    DailyOrderCounter,
    Order,
    OrderItem,
    OrderType,
)


class OrderModelTest(TestCase):

    def setUp(self):
        self.order_type = OrderType.objects.create(
            name="حضوری - بیرون بر"
        )

    def test_create_order(self):
        order = Order.objects.create(
            order_date=date(2026, 8, 22),
            order_number=100,
            order_type=self.order_type,
            packaging_cost=20000,
            discount=10000,
            tax=5000,
            total_price=315000,
        )

        self.assertEqual(order.order_number, 100)
        self.assertEqual(
            order.order_date,
            date(2026, 8, 22)
        )

        self.assertEqual(
            order.packaging_cost,
            20000
        )

        self.assertEqual(
            order.discount,
            10000
        )

        self.assertEqual(
            order.tax,
            5000
        )

        self.assertEqual(
            order.total_price,
            315000
        )

    def test_order_str(self):
        order = Order.objects.create(
            order_date=date(2026, 8, 22),
            order_number=100,
            order_type=self.order_type,
        )

        self.assertEqual(
            str(order),
            "سفارش #100"
        )

    def test_order_default_values(self):
        order = Order.objects.create(
            order_date=date(2026, 8, 22),
            order_number=100,
            order_type=self.order_type,
        )

        self.assertEqual(order.discount, 0)
        self.assertEqual(order.tax, 0)
        self.assertEqual(order.packaging_cost, 0)
        self.assertEqual(order.total_price, 0)
        self.assertIsNone(order.table_number)

    def test_order_with_table_number(self):
        order = Order.objects.create(
            order_date=date(2026, 8, 22),
            order_number=100,
            order_type=self.order_type,
            table_number=12,
        )

        self.assertEqual(
            order.table_number,
            12
        )

    def test_table_number_is_optional(self):
        order = Order.objects.create(
            order_date=date(2026, 8, 22),
            order_number=100,
            order_type=self.order_type,
        )

        self.assertIsNone(
            order.table_number
        )

    def test_order_number_must_be_unique_per_day(self):
        Order.objects.create(
            order_date=date(2026, 8, 22),
            order_number=100,
            order_type=self.order_type,
        )

        with self.assertRaises(IntegrityError):
            Order.objects.create(
                order_date=date(2026, 8, 22),
                order_number=100,
                order_type=self.order_type,
            )

    def test_same_order_number_can_be_used_on_different_days(self):
        order1 = Order.objects.create(
            order_date=date(2026, 8, 22),
            order_number=100,
            order_type=self.order_type,
        )

        order2 = Order.objects.create(
            order_date=date(2026, 8, 23),
            order_number=100,
            order_type=self.order_type,
        )

        self.assertEqual(order1.order_number, 100)
        self.assertEqual(order2.order_number, 100)

