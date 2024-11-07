from django.test import TestCase
from tutorials.models import User
from libgravatar import Gravatar

class UserModelTest(TestCase):
    
    def setUp(self):
        """Set up test users."""
        self.admin_user = User.objects.create_user(
            username='@adminuser',
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            password='Password123',
            role='admin'
        )
        
        self.tutor_user = User.objects.create_user(
            username='@tutoruser',
            first_name='Tutor',
            last_name='User',
            email='tutor@example.com',
            password='Password123',
            role='tutor',
            expertise='Python, Django'
        )
        
        self.student_user = User.objects.create_user(
            username='@studentuser',
            first_name='Student',
            last_name='User',
            email='student@example.com',
            password='Password123',
            role='student',
            lesson_preferences='Python Basics'
        )

    def test_full_name(self):
        """Test the full_name method."""
        self.assertEqual(self.admin_user.full_name(), 'Admin User')
        self.assertEqual(self.tutor_user.full_name(), 'Tutor User')
        self.assertEqual(self.student_user.full_name(), 'Student User')

    def test_gravatar_url(self):
        """Test that gravatar URLs are generated correctly."""
        gravatar_url = Gravatar(self.admin_user.email).get_image(size=120, default='mp')
        self.assertEqual(self.admin_user.gravatar(120), gravatar_url)

    def test_mini_gravatar_url(self):
        """Test the mini_gravatar method."""
        mini_gravatar_url = Gravatar(self.student_user.email).get_image(size=60, default='mp')
        self.assertEqual(self.student_user.mini_gravatar(), mini_gravatar_url)

    def test_role_field(self):
        """Test role field values."""
        self.assertEqual(self.admin_user.role, 'admin')
        self.assertEqual(self.tutor_user.role, 'tutor')
        self.assertEqual(self.student_user.role, 'student')

    def test_expertise_field(self):
        """Test expertise field for tutors."""
        self.assertEqual(self.tutor_user.expertise, 'Python, Django')
        self.assertIsNone(self.admin_user.expertise)

    def test_lesson_preferences_field(self):
        """Test lesson preferences field for students."""
        self.assertEqual(self.student_user.lesson_preferences, 'Python Basics')
        self.assertIsNone(self.tutor_user.lesson_preferences)

    def test_default_ordering(self):
        """Test that the default ordering works correctly."""
        users = User.objects.all()
        self.assertQuerysetEqual(
            users, 
            [self.admin_user, self.student_user, self.tutor_user], 
            transform=lambda x: x 
        )
