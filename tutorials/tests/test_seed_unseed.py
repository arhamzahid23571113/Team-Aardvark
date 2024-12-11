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
        self.assertEqual(users.count(), 54)  # 50 random users + 3 predefined + 1 admin

        # Test lesson requests
        lesson_requests = LessonRequest.objects.all()
        self.assertGreater(lesson_requests.count(), 0)

        # Test lesson bookings
        lesson_bookings = LessonBooking.objects.all()
        self.assertEqual(lesson_bookings.count(), 100)  # Update if required

        # Test invoices
        invoices = Invoice.objects.all()
        self.assertGreater(invoices.count(), 0)

    def test_seed_and_unseed_work_together(self):
        """Test the full workflow of seeding and unseeding."""
        call_command('seed')
        self.assertGreater(User.objects.filter(role__in=['student', 'tutor']).count(), 0)
        call_command('unseed')
        self.assertEqual(User.objects.filter(role__in=['student', 'tutor']).count(), 0)

    def test_unseed_removes_all_seeded_data(self):
        """Test that the unseed command removes all seeded data."""
        call_command('seed')
        call_command('unseed')
        self.assertEqual(User.objects.filter(role__in=['student', 'tutor']).count(), 0)
        self.assertEqual(LessonRequest.objects.count(), 0)
        self.assertEqual(LessonBooking.objects.count(), 0)
        self.assertEqual(Invoice.objects.count(), 0)
