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


class OrderTypeModelTest(TestCase):

    def test_order_type_str(self):
        order_type = OrderType.objects.create(
            name="حضوری - داخل سالن"
        )

        self.assertEqual(
            str(order_type),
            "حضوری - داخل سالن"
        )

    def test_order_type_is_active_by_default(self):
        order_type = OrderType.objects.create(
            name="حضوری - بیرون بر"
        )

        self.assertTrue(order_type.is_active)


class DailyOrderCounterModelTest(TestCase):

    def test_daily_order_counter_str(self):
        counter = DailyOrderCounter.objects.create(
            date=date(2026, 8, 22),
            last_number=150,
        )

        self.assertEqual(
            str(counter),
            "2026-08-22 - 150"
        )

    def test_last_number_default(self):
        counter = DailyOrderCounter.objects.create(
            date=date(2026, 8, 22),
        )

        self.assertEqual(
            counter.last_number,
            99
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


class OrderItemModelTest(TestCase):

    def setUp(self):
        self.order_type = OrderType.objects.create(
            name="حضوری - داخل سالن"
        )

        self.order = Order.objects.create(
            order_date=date(2026, 8, 22),
            order_number=100,
            order_type=self.order_type,
        )

        self.category = Category.objects.create(
            title="ساندویچ"
        )

        self.menu_item = MenuItem.objects.create(
            category=self.category,
            name="همبرگر ویژه",
            price=150000,
        )

    def test_order_item_str(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            quantity=2,
            unit_price=150000,
            total_price=300000,
        )

        self.assertEqual(
            str(order_item),
            "همبرگر ویژه × 2"
        )

    def test_order_item_values(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            quantity=2,
            unit_price=150000,
            total_price=300000,
        )

        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.unit_price, 150000)
        self.assertEqual(order_item.total_price, 300000)

    def test_order_items_relation(self):
        OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            quantity=2,
            unit_price=150000,
            total_price=300000,
        )

        self.assertEqual(
            self.order.items.count(),
            1
        )


class OrderNumberServiceTest(TestCase):

    def test_first_order_number_of_day(self):
        number = get_next_order_number()

        self.assertEqual(
            number,
            100
        )

    def test_next_order_number(self):
        first = get_next_order_number()
        second = get_next_order_number()
        third = get_next_order_number()

        self.assertEqual(first, 100)
        self.assertEqual(second, 101)
        self.assertEqual(third, 102)

    def test_counter_is_created_for_today(self):
        get_next_order_number()

        self.assertEqual(
            DailyOrderCounter.objects.count(),
            1
        )

        counter = DailyOrderCounter.objects.first()

        self.assertEqual(
            counter.last_number,
            100
        )