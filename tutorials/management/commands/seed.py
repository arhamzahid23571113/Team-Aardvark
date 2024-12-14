from django.core.management.base import BaseCommand
from tutorials.models import User, LessonRequest, LessonBooking, Invoice
from faker import Faker
from random import choice, randint
import uuid
import random

faker = Faker('en_GB')

class Command(BaseCommand):
    """Seed the database with sample data for testing."""

    DEFAULT_PASSWORD = 'Password123'
    USER_COUNT = 50

    def handle(self, *args, **kwargs):
        """Main method to handle seeding."""
        self.stdout.write("Clearing existing data...")
        User.objects.all().delete()
        LessonRequest.objects.all().delete()
        LessonBooking.objects.all().delete()
        Invoice.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Existing data cleared."))

        self.create_admin_user()
        self.create_predefined_users()
        self.create_random_users()
        self.create_lesson_requests()
        self.create_lesson_bookings()
        self.create_invoices()

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))

    def create_admin_user(self):
        """Create the admin user."""
        if not User.objects.filter(username='@admin', email='admin@example.com').exists():
            admin = User.objects.create_superuser(
                username='@admin',
                email='admin@example.com',
                password=self.DEFAULT_PASSWORD,
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS(f"Admin user (@admin) created."))
        else:
            self.stdout.write("Admin user already exists. Skipping creation.")

    def create_predefined_users(self):
        """Create predefined users."""
        predefined_users = [
            {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'role': 'tutor'},
            {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'role': 'tutor'},
            {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'role': 'student'},
        ]
        for user_data in predefined_users:
            User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=self.DEFAULT_PASSWORD,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role']
            )
            self.stdout.write(self.style.SUCCESS(f"User {user_data['username']} created."))

    def create_random_users(self):
        """Create random users."""
        for _ in range(self.USER_COUNT):
            role = choice(['tutor', 'student'])
            username = f"@{faker.first_name().lower()}{uuid.uuid4().hex[:6]}"
            email = f"{username}@example.com"
            User.objects.create_user(
                username=username,
                email=email,
                password=self.DEFAULT_PASSWORD,
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                role=role,
                expertise="Python, JavaScript" if role == 'tutor' else None
            )
        self.stdout.write(self.style.SUCCESS(f"{self.USER_COUNT} random users created."))

    def create_lesson_requests(self):
        """Seed lesson requests."""
        students = User.objects.filter(role='student')
        tutors = User.objects.filter(role='tutor')
        for student in students:
            LessonRequest.objects.create(
                student=student,
                tutor=choice(tutors) if tutors.exists() else None,
                status=choice(['Unallocated', 'Allocated', 'Cancelled']),
                requested_topic=faker.word(),
                requested_frequency=choice(["Weekly", "Fortnightly"]),
                requested_duration=choice([30, 60, 90]),
                requested_time=faker.time(),
                preferred_day=choice(["Monday", "Tuesday", "Wednesday"]),
                experience_level=choice(["No Experience", "Beginner", "Intermediate"]),
                additional_notes=faker.text(max_nb_chars=50),
            )
        self.stdout.write(self.style.SUCCESS("Lesson requests created."))

    def create_lesson_bookings(self):
        """Seed lesson bookings."""
        students = User.objects.filter(role='student')
        tutors = User.objects.filter(role='tutor')
        for _ in range(100):  # Update from 50 to 100
            student = choice(students)
            tutor = choice(tutors) if tutors.exists() else None
            LessonBooking.objects.create(
                student=student,
                tutor=tutor,
                topic=faker.word(),
                duration=choice([30, 60, 90]),
                time=faker.time(),
                lesson_date=faker.date_between(start_date='-30d', end_date='+30d'),
                frequency=choice(["Weekly", "Fortnightly"]),
                preferred_day=choice(["Monday", "Tuesday", "Wednesday"]),
                experience_level=choice(["Beginner", "Intermediate"]),
                additional_notes=faker.text(max_nb_chars=50),
            )
        self.stdout.write(self.style.SUCCESS("100 Lesson bookings created."))


    def create_lesson_bookings(self):
        """Seed lesson bookings."""
        print("Creating lesson bookings...")
        students = User.objects.filter(role='student')
        tutors = User.objects.filter(role='tutor')
        for _ in range(100):  # Example: 100 bookings
            student = random.choice(students)
            tutor = random.choice(tutors)
            LessonBooking.objects.create(
                student=student,
                tutor=tutor,
                topic=random.choice(["Python Programming", "Web Development"]),
                duration=random.choice([30, 60, 90, 120]),
                time=faker.time(),
                lesson_date=faker.date_between(start_date='-30d', end_date='+30d'),
                frequency=random.choice(["Weekly", "Fortnightly"]),
                preferred_day=random.choice(["Monday", "Tuesday", "Wednesday"]),
                experience_level=random.choice(["Beginner", "Intermediate"]),
                additional_notes=faker.text(max_nb_chars=50),
            )
        print("Lesson bookings created.")

    def create_invoices(self):
        """Seed invoices."""
        students = User.objects.filter(role='student')
        for student in students:
            Invoice.objects.create(
                invoice_num=f"INV{randint(100000, 999999)}",
                student=student,
                due_date=faker.date_between(start_date='-30d', end_date='+30d'),
                payment_status=choice(['Paid', 'Unpaid']),
            )
        self.stdout.write(self.style.SUCCESS("Invoices created."))

