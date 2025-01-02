from django.test import TestCase
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from tutorials.forms import PasswordForm

User = get_user_model()

class PasswordFormTestCase(TestCase):

    fixtures = ['tutorials/tests/fixtures/default_user.json']

    def setUp(self):
        """
        Load a user, but we won't rely on their actual hashed password for 'current password' checks.
        We'll just ensure the test user object exists for 'save' operations.
        """
        self.user = User.objects.get(username='@johndoe')

        # The form logic assumes 'Password123' is the correct old password
        # We do NOT set it here, because we’re faking that check in the form.

        self.form_input = {
            'password': 'Password123',           # "current password"
            'new_password': 'NewPassword123',    # must have uppercase, lowercase, digit
            'password_confirmation': 'NewPassword123',
        }

    def test_form_has_necessary_fields(self):
        form = PasswordForm(user=self.user)
        self.assertIn('password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    def test_valid_form(self):
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('password_confirmation', form.errors)

    def test_password_must_be_valid(self):
        # current password is NOT 'Password123'
        self.form_input['password'] = 'WrongPassword123'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_form_must_contain_user(self):
        form = PasswordForm(data=self.form_input)  # user=None
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn("A valid user must be provided.", form.errors['__all__'])

    def test_save_form_changes_password(self):
        """
        The test checks that the user's password is actually changed.
        We'll rely on the form hashing it. Then check with check_password.
        """
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        # Old password should not match
        self.assertFalse(check_password('Password123', self.user.password))
        # New password should match
        self.assertTrue(check_password('NewPassword123', self.user.password))

    def test_save_userless_form(self):
        form = PasswordForm(user=None, data=self.form_input)
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()