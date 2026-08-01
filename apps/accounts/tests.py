from django.test import TestCase
from django.db import IntegrityError

from .models import Customer, Employee, Role


class RoleModelTest(TestCase):

    def test_create_role(self):
        role = Role.objects.create(title="مدیر")

        self.assertEqual(role.title, "مدیر")

    def test_role_str(self):
        role = Role.objects.create(title="صندوق دار")

        self.assertEqual(str(role), "صندوق دار")


class EmployeeModelTest(TestCase):

    def setUp(self):
        self.role = Role.objects.create(title="مدیر")

    def test_create_employee(self):

        employee = Employee.objects.create(
            role=self.role,
            first_name="علی",
            last_name="احمدی",
            mobile="09123456789",
        )

        self.assertEqual(employee.first_name, "علی")
        self.assertEqual(employee.last_name, "احمدی")

    def test_employee_str(self):

        employee = Employee.objects.create(
            role=self.role,
            first_name="رضا",
            last_name="کریمی",
            mobile="09120000000",
        )

        self.assertEqual(str(employee), "رضا کریمی")

    def test_default_balance(self):

        employee = Employee.objects.create(
            role=self.role,
            first_name="محمد",
            last_name="رحیمی",
            mobile="09121111111",
        )

        self.assertEqual(employee.balance, 0)

    def test_default_status(self):

        employee = Employee.objects.create(
            role=self.role,
            first_name="حسن",
            last_name="محمدی",
            mobile="09122222222",
        )

        self.assertEqual(
            employee.status,
            Employee.EmploymentStatus.ACTIVE
        )

    def test_employee_role_relation(self):

        employee = Employee.objects.create(
            role=self.role,
            first_name="اکبر",
            last_name="صادقی",
            mobile="09123333333",
        )

        self.assertEqual(employee.role.title, "مدیر")


class CustomerModelTest(TestCase):

    def test_create_customer(self):

        customer = Customer.objects.create(
            subscription_code="1001",
            name="علی رضایی",
            mobile="09124444444",
        )

        self.assertEqual(customer.name, "علی رضایی")

    def test_customer_str(self):

        customer = Customer.objects.create(
            subscription_code="1002",
            name="محمد کریمی",
            mobile="09125555555",
        )

        self.assertEqual(
            str(customer),
            "1002 محمد کریمی"
        )

    def test_default_balance(self):

        customer = Customer.objects.create(
            subscription_code="1003",
            name="رضا احمدی",
            mobile="09126666666",
        )

        self.assertEqual(customer.balance, 0)

    def test_mobile_is_unique(self):

        Customer.objects.create(
            subscription_code="1004",
            name="علی",
            mobile="09127777777",
        )

        with self.assertRaises(IntegrityError):
            Customer.objects.create(
                subscription_code="1005",
                name="رضا",
                mobile="09127777777",
            )

    def test_subscription_code_is_unique(self):

        Customer.objects.create(
            subscription_code="1006",
            name="علی",
            mobile="09128888888",
        )

        with self.assertRaises(IntegrityError):
            Customer.objects.create(
                subscription_code="1006",
                name="محمد",
                mobile="09129999999",
            )
