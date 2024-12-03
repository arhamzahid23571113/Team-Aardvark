from django.core.management.base import BaseCommand
from tutorials.models import User, LessonRequest, LessonBooking, Invoice

class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Unseeds the database by removing all seeded data'

    def handle(self, *args, **options):
        """Unseed the database."""
        # Remove invoices
        Invoice.objects.all().delete()
        self.stdout.write("All invoices removed.")

        # Remove lesson bookings
        LessonBooking.objects.all().delete()
        self.stdout.write("All lesson bookings removed.")

        # Remove lesson requests
        LessonRequest.objects.all().delete()
        self.stdout.write("All lesson requests removed.")

        # Remove non-staff users
        User.objects.filter(is_staff=False).delete()
        self.stdout.write("All non-staff users removed.")

        self.stdout.write("Database unseeding complete.")
