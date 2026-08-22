from django.test import TestCase

from .models import Category, MenuItem, MenuItemVariant


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
            name="همبرگر",
            category=self.category,
        )

        self.assertEqual(item.name, "همبرگر")
        self.assertEqual(item.category, self.category)

    def test_str(self):
        item = MenuItem.objects.create(
            name="هات داگ",
            category=self.category,
        )

        self.assertEqual(str(item), "هات داگ")

    def test_default_is_available(self):
        item = MenuItem.objects.create(
            name="همبرگر",
            category=self.category,
        )

        self.assertTrue(item.is_available)

    def test_default_is_active(self):
        item = MenuItem.objects.create(
            name="همبرگر",
            category=self.category,
        )

        self.assertTrue(item.is_active)


class MenuItemVariantModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            title="ساندویچ"
        )

        self.menu_item = MenuItem.objects.create(
            name="همبرگر",
            category=self.category,
        )

    def test_create_variant(self):
        variant = MenuItemVariant.objects.create(
            menu_item=self.menu_item,
            name="با پنیر",
            price=150000,
        )

        self.assertEqual(variant.menu_item, self.menu_item)
        self.assertEqual(variant.name, "با پنیر")
        self.assertEqual(variant.price, 150000)

    def test_str(self):
        variant = MenuItemVariant.objects.create(
            menu_item=self.menu_item,
            name="با قارچ و پنیر",
            price=180000,
        )

        self.assertEqual(
            str(variant),
            "همبرگر - با قارچ و پنیر"
        )

    def test_default_is_available(self):
        variant = MenuItemVariant.objects.create(
            menu_item=self.menu_item,
            name="ساده",
            price=120000,
        )

        self.assertTrue(variant.is_available)

    def test_default_is_active(self):
        variant = MenuItemVariant.objects.create(
            menu_item=self.menu_item,
            name="اقتصادی",
            price=100000,
        )

        self.assertTrue(variant.is_active)

    def test_multiple_variants(self):
        MenuItemVariant.objects.create(
            menu_item=self.menu_item,
            name="ساده",
            price=120000,
        )

        MenuItemVariant.objects.create(
            menu_item=self.menu_item,
            name="با پنیر",
            price=140000,
        )

        MenuItemVariant.objects.create(
            menu_item=self.menu_item,
            name="با قارچ و پنیر",
            price=170000,
        )

        self.assertEqual(
            self.menu_item.variants.count(),
            3
        )