from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from tutorials.models import User
from tutorials.models import Tutor, Student
import pytz
from faker import Faker
from random import randint, random

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

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

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'
