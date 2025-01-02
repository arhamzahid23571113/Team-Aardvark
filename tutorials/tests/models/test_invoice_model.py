"""Unit tests for the Invoice model"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from datetime import date, timedelta
from tutorials.models import Invoice
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class InvoiceModelTestCases(TestCase):
    """Unit tests for the invoice model"""
    
    def setUp(self):
        self.valid_student = User.objects.create(
            username="@ben",
            first_name="Ben",
            last_name="Doe",
            email="ben@gmail.com",
            role='student',
            expertise=None
        )

        self.invoice = Invoice.objects.create(
            student=self.valid_student,
            invoice_num="INV51143",
            due_date=date.today() + timedelta(days=14), #14 days from the current date
            #invoice date is automatically added
            payment_status = 'Unpaid',
            payment_date=None
        )

    def test_valid_invoice_is_valid(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail("The default test invoice should be valid")
    
    #Student Field Tests
    def test_invoice_with_no_student_is_invalid(self):
        self.invoice.student = None
        self._assert_invoice_is_invalid()

    def test_invoice_with_tutor_as_student_is_invalid(self):
        self.invoice.student.role = 'tutor'
        self.invoice.student.save()
        self._assert_invoice_is_invalid()

    def test_invoice_with_admin_as_student_is_invalid(self):
        self.invoice.student.role = 'admin'
        self.invoice.student.save()
        self._assert_invoice_is_invalid()

    def test_invoice_with_deleted_student_is_invalid(self):
        student = self.invoice.student
        student.delete()
        self._assert_invoice_is_invalid()

    #DateField tests
    def test_invoice_with_due_date_before_invoice_date_is_invalid(self):
        self.invoice.invoice_date = date(2024, 11, 30)
        self.invoice.due_date = date(2024, 11, 20)
        self._assert_invoice_is_invalid()

    def test_invoice_with_due_date_after_invoice_date_is_valid(self):
        self.invoice.invoice_date = date(2024, 11, 20)
        self.invoice.due_date = date(2024, 11, 30)
        self._assert_invoice_is_valid()

    def test_invoice_with_payment_date_after_due_date_is_valid(self):
        #Admins will personally deal with late payments.
        self.invoice.payment_date = date.today() + timedelta(days=20)
        self.invoice.payment_status = "Paid"
        self._assert_invoice_is_valid()

    def test_invoice_date_is_automatically_set_on_creation(self):
        test_invoice = Invoice.objects.create(
            student=self.valid_student,
            invoice_num = "INV54243",
            due_date = date.today() + timedelta(days=20),
            payment_status = 'Unpaid'
        )
        self.assertIsNotNone(test_invoice.invoice_date)
        #make sure that the invoice date is the same as date of invoice creation
        self.assertEqual(test_invoice.invoice_date, date.today()) 

    #Payment status field tests
    def test_invoice_with_invalid_payment_status_is_invalid(self):
        self.invoice.payment_status = 'Unknown'
        self._assert_invoice_is_invalid()
    
    def test_invoice_with_paid_status_and_missing_payment_date_is_invalid(self):
        self.invoice.payment_status = 'Paid'
        self.invoice.payment_date = None
        self._assert_invoice_is_invalid()
    
    def test_invoice_with_payment_date_and_unpaid_payment_status_is_invalid(self):
        self.invoice.payment_status = 'Unpaid'
        self.invoice.payment_date = date.today()
        self._assert_invoice_is_invalid()

    def test_invoice_with_paid_payment_status_and_existing_payment_date_is_valid(self):
        self.invoice.payment_status = 'Paid'
        self.invoice.payment_date = date.today()
        self._assert_invoice_is_valid()

    def test_deleting_student_deletes_invoices(self):
        student = self.valid_student
        test_invoice = Invoice.objects.create(
            student = student,
            invoice_num="INV23456",
            due_date = date.today() + timedelta(days=30),
            payment_status = 'Unpaid'
        )
        student.delete()
        invoice_exists = Invoice.objects.filter(id=test_invoice.id).exists()
        self.assertFalse(invoice_exists)

    #Invoice num tests
    #test invoice model already has 8 characters
    def test_invoice_num_more_than_8_char_is_invalid(self):
        self.invoice.invoice_num = "INV123456"
        self._assert_invoice_is_invalid()

    def test_invoice_num_less_than_max_is_valid(self):
        self.invoice.invoice_num = "INV1"
        self._assert_invoice_is_valid()

    def test_invoice_num_is_unique(self):
        #invoice num must be unique
        with self.assertRaises(ValidationError):
                Invoice.objects.create(
                    student=self.valid_student,
                    invoice_num="INV51143", #duplicate invoice num
                    due_date=date.today() + timedelta(days=10),
                    payment_status="Unpaid"
                )

    def test_invoice_num_cannot_be_blank(self):
        #Test that invoice_num cannot be blank
        with self.assertRaises(ValidationError):
                Invoice.objects.create(
                    student=self.valid_student,
                    invoice_num='',
                    due_date=date.today() + timedelta(days=10),
                    payment_status='Unpaid'
                )

    def test_invoice_num_cannot_be_null(self):
        with self.assertRaises(ValidationError):
            Invoice.objects.create(
                student=self.valid_student,
                invoice_num=None,
                due_date=date.today() + timedelta(days=10),
                payment_status="Unpaid"
            )
            
    #str method test
    def test_str_method_works(self):
        expected_str = f"Invoice INV51143 for Ben Doe"
        self.assertEqual(str(self.invoice), expected_str)

    #Helper methods
    def _assert_invoice_is_valid(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail("The test invoice should be valid")

    def _assert_invoice_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()
    