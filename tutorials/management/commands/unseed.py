from django.core.management.base import BaseCommand
from tutorials.models import User, LessonRequest, LessonBooking, Invoice,ContactMessage

class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Unseeds the database by removing all seeded data'

    def handle(self, *args, **options):
        """Unseed the database."""
        # Remove invoices
        Invoice.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All invoices removed."))

        # Remove lesson bookings
        LessonBooking.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All lesson bookings removed."))

        # Remove lesson requests
        LessonRequest.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All lesson requests removed."))

        ContactMessage.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All contact messages removed."))

        # Remove predefined users (e.g., @johndoe, @janedoe, @charlie)
        User.objects.filter(username__in=['@johndoe', '@janedoe', '@charlie']).delete()
        self.stdout.write(self.style.SUCCESS("All predefined users removed."))

        # Remove non-staff users with a specific email pattern
        User.objects.filter(is_staff=False, email__endswith='@example.com').delete()
        self.stdout.write(self.style.SUCCESS("All seeded users removed."))

        self.stdout.write(self.style.SUCCESS("Database unseeding complete."))
       