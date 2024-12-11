from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from tutorials.models import User, LessonRequest, Invoice
from tutorials.models import Tutor, Student
import pytz
from faker import Faker
from random import randint, random
import random
import uuid


user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]
import random
from datetime import timedelta, date
import uuid

faker = Faker('en_GB')

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    """Seed the database with sample data."""
    
    DEFAULT_PASSWORD = 'Password123'
    USER_COUNT = 50  # Example count for students and tutors

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **kwargs):
   
        User.objects.all().delete()

  
        self.generate_user_fixtures()
        self.stdout.write(self.style.SUCCESS("Predefined users created."))

        
        john_doe = User.objects.create_user(username="johndoe", password="Password123")
        john_doe.is_staff = True
        john_doe.is_superuser = True
        john_doe.save()
        self.stdout.write(self.style.SUCCESS(f"Admin user (@johndoe) created"))

        
        jane_doe = User.objects.create_user(username="janedoe", password="Password123")
        tutor = Tutor.objects.create(user=jane_doe)
        self.stdout.write(self.style.SUCCESS(f"Tutor user (@janedoe) created"))

    
        charlie = User.objects.create_user(username="charlie", password="Password123")
        Student.objects.create(user=charlie, tutor=tutor)
        self.stdout.write(self.style.SUCCESS(f"Student user (@charlie) created"))

    
        self.generate_random_users()

        
        self.stdout.write(self.style.SUCCESS("Seeding completed successfully!"))


    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def create_username(self, first_name, last_name):
        return '@' + first_name.lower() + last_name.lower()

    def create_email(self, first_name, last_name):
        print("Creating users...")
        faker = Faker()  # Initialize Faker instance
        roles = ['student', 'tutor']
        
        for i in range(self.USER_COUNT):
            role = random.choice(roles)
            username = f"@{faker.first_name().lower()}{i}"
            # Ensure unique email by appending a UUID
            email = f"{username}{uuid.uuid4().hex[:6]}@example.com"
            expertise = "Python, JavaScript" if role == 'tutor' else None
            User.objects.create_user(
                username=username,
                email=email,
                password=self.DEFAULT_PASSWORD,
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                role=role,
                expertise=expertise,
            )

        if not User.objects.filter(username='@admin', email='admin@example.com').exists():
            User.objects.create_superuser(
                username='@admin',
                email='admin@example.com',
                password=self.DEFAULT_PASSWORD,
                first_name='Admin',
                last_name='User',
            )
            print("Admin user created.")
        else:
            print("Admin user already exists. Skipping creation.")

        print("Users created.")
        return f"{first_name.lower()}.{last_name.lower()}@example.org"

    def create_lesson_requests(self):
        """Seed lesson requests."""
        print("Creating lesson requests...")
        students = User.objects.filter(role='student')
        tutors = User.objects.filter(role='tutor')
        for student in students:
            LessonRequest.objects.create(
                student=student,
                tutor=random.choice(tutors) if random.random() > 0.5 else None,
                status=random.choice(['Unallocated', 'Allocated', 'Pending', 'Cancelled']),
                requested_topic=random.choice(["Python Programming", "Web Development", "Ruby on Rails","AI and Machine Learning"]),
                requested_frequency=random.choice(["Weekly", "Fortnightly"]),
                requested_duration=random.choice([30, 60, 90, 120]),
                requested_date = faker.date(),
                requested_time=faker.time(),
                experience_level=random.choice(["No Experience", "Beginner", "Intermediate", "Advanced"]),
                additional_notes=faker.text(max_nb_chars=50),
            )
        print("Lesson requests created.")


    def create_invoices(self):
        """Seed invoices."""
        print("Creating invoices...")
        students = User.objects.filter(role='student')
        for student in students:
            Invoice.objects.create(
                student=student,
                amount_due=random.uniform(50, 500),
                due_date=faker.date_between(start_date='-30d', end_date='+30d'),
                payment_status=random.choice(['Paid', 'Unpaid']),
            )
        print("Invoices created.")

