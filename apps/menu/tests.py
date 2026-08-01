from django.test import TestCase
from .models import Category, MenuItem


class CategoryModelTest(TestCase):

    def test_str(self):
        category = Category.objects.create(
            title="پیتزا"
        )

        self.assertEqual(str(category), "پیتزا")

    def test_default_is_active(self):
        category = Category.objects.create(
            title="نوشیدنی"
        )

        self.assertTrue(category.is_active)


class MenuItemModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            title="ساندویچ"
        )

    def test_create_menu_item(self):
        item = MenuItem.objects.create(
            name="همبرگر مخصوص",
            category=self.category,
            price=250000
        )

        self.assertEqual(item.name, "همبرگر مخصوص")
        self.assertEqual(item.category, self.category)
        self.assertEqual(item.price, 250000)

    def test_str(self):
        item = MenuItem.objects.create(
            name="هات داگ",
            category=self.category,
            price=180000
        )

        self.assertEqual(str(item), "هات داگ")

    def test_default_is_available(self):
        item = MenuItem.objects.create(
            name="پیتزا مخلوط",
            category=self.category,
            price=300000
        )

        self.assertTrue(item.is_available)

    def test_default_is_active(self):
        item = MenuItem.objects.create(
            name="پیتزا مخصوص",
            category=self.category,
            price=320000
        )

        self.assertTrue(item.is_active)

