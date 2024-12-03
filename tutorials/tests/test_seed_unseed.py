from django.core.management import call_command
from django.test import TestCase
from tutorials.models import User, LessonRequest, LessonBooking, Invoice

class SeedUnseedTests(TestCase):
    """Test suite for database seeding and unseeding."""

    def test_seed_creates_expected_data(self):
        """Test that the seed command populates the database correctly."""
        call_command('seed')

        # Test user creation
        users = User.objects.all()
        self.assertGreaterEqual(users.count(), 51)  # 50 users + 1 admin
        admin_user = User.objects.filter(username='@admin', email='admin@example.com').first()
        self.assertIsNotNone(admin_user)
        self.assertTrue(admin_user.is_staff)

        # Test lesson requests
        lesson_requests = LessonRequest.objects.all()
        self.assertGreater(lesson_requests.count(), 0)

        # Test lesson bookings
        lesson_bookings = LessonBooking.objects.all()
        self.assertEqual(lesson_bookings.count(), 100)

        # Test invoices
        invoices = Invoice.objects.all()
        self.assertGreater(invoices.count(), 0)

    def test_seed_ensures_unique_emails(self):
        """Test that the seed command generates unique emails."""
        call_command('seed')
        emails = User.objects.values_list('email', flat=True)
        self.assertEqual(len(emails), len(set(emails)))  # No duplicate emails

    def test_unseed_removes_all_seeded_data(self):
        """Test that the unseed command removes all seeded data."""
        # Run seed first
        call_command('seed')

        # Run unseed
        call_command('unseed')

        # Verify database is cleaned
        self.assertEqual(User.objects.filter(is_staff=False).count(), 0)
        self.assertEqual(LessonRequest.objects.count(), 0)
        self.assertEqual(LessonBooking.objects.count(), 0)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_seed_and_unseed_work_together(self):
        """Test the full workflow of seeding and unseeding."""
        # Seed the database
        call_command('seed')

        # Verify data was created
        self.assertGreater(User.objects.filter(is_staff=False).count(), 0)
        self.assertGreater(LessonRequest.objects.count(), 0)
        self.assertGreater(LessonBooking.objects.count(), 0)
        self.assertGreater(Invoice.objects.count(), 0)

        # Unseed the database
        call_command('unseed')

        # Verify data was removed
        self.assertEqual(User.objects.filter(is_staff=False).count(), 0)
        self.assertEqual(LessonRequest.objects.count(), 0)
        self.assertEqual(LessonBooking.objects.count(), 0)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_admin_user_is_not_deleted(self):
        """Test that the admin user is not removed during unseeding."""
        call_command('seed')
        call_command('unseed')

        # Verify admin user still exists
        admin_user = User.objects.filter(username='@admin', email='admin@example.com').first()
        self.assertIsNotNone(admin_user)
        self.assertTrue(admin_user.is_staff)

    def test_no_duplicate_admin_user_on_reseed(self):
        """Test that reseeding does not create duplicate admin users."""
        call_command('seed')  # First seed
        call_command('seed')  # Reseed

        # Verify only one admin user exists
        admin_users = User.objects.filter(username='@admin', email='admin@example.com')
        self.assertEqual(admin_users.count(), 1)

    def test_seed_generates_expected_roles(self):
        """Test that seeded users have the correct roles."""
        call_command('seed')

        # Verify roles
        students = User.objects.filter(role='student')
        tutors = User.objects.filter(role='tutor')
        self.assertGreater(students.count(), 0)
        self.assertGreater(tutors.count(), 0)
