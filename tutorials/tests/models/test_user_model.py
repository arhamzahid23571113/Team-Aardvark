"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User

class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    GRAVATAR_URL = "https://www.gravatar.com/avatar/363c1b0cd64dadffb867236a00e62986"

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

    def test_valid_user(self):
        self._assert_user_is_valid()

    # Username Tests
    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_can_be_30_characters_long(self):
        self.user.username = '@' + 'x' * 29
        self._assert_user_is_valid()

    def test_username_cannot_be_over_30_characters_long(self):
        self.user.username = '@' + 'x' * 30
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.username = second_user.username
        self._assert_user_is_invalid()

    # First Name Tests
    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    # Last Name Tests
    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    # Email Tests
    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    # Role Field Tests
    def test_valid_roles(self):
        for role in ['admin', 'tutor', 'student']:
            self.user.role = role
            self._assert_user_is_valid()

    def test_invalid_role(self):
        self.user.role = 'invalid_role'
        self._assert_user_is_invalid()

    # Expertise Field Tests
    def test_expertise_can_be_blank(self):
        self.user.expertise = ''
        self._assert_user_is_valid()

    def test_expertise_can_contain_topics(self):
        self.user.expertise = 'Python, Django'
        self._assert_user_is_valid()

    # Lesson Preferences Field Tests
    def test_lesson_preferences_can_be_blank(self):
        self.user.lesson_preferences = ''
        self._assert_user_is_valid()

    def test_lesson_preferences_can_contain_preferences(self):
        self.user.lesson_preferences = 'Python Basics'
        self._assert_user_is_valid()

    # Custom Methods Tests
    def test_full_name_must_be_correct(self):
        self.assertEqual(self.user.full_name(), "John Doe")

    def test_default_gravatar(self):
        self.assertEqual(self.user.gravatar(), self._gravatar_url(size=120))

    def test_custom_gravatar(self):
        self.assertEqual(self.user.gravatar(size=100), self._gravatar_url(size=100))

    def test_mini_gravatar(self):
        self.assertEqual(self.user.mini_gravatar(), self._gravatar_url(size=60))

    # Helper Methods
    def _gravatar_url(self, size):
        return f"{UserModelTestCase.GRAVATAR_URL}?size={size}&default=mp"

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
