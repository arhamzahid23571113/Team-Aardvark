from django import forms
from django.test import TestCase
from tutorials.forms import UserForm
from tutorials.models import User

class UserFormTestCase(TestCase):
    """Unit tests of the user form."""

    fixtures = ['tutorials/tests/fixtures/default_user.json']

    def setUp(self):
        # Include 'role' and (optionally) an empty 'profile_picture' to avoid validation issues.
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',             # Must match the model's regex: ^@\w{3,}$
            'email': 'janedoe@example.org',     # Must be unique if the fixture doesn't already use it
            'role': 'student',                  # Provide a valid choice from ('admin', 'tutor', 'student')
            'profile_picture': '',              # Avoid file validation if needed
            'expertise': ''                     # It's optional, so you can leave it blank
        }

    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

    def test_valid_user_form(self):
        """
        With the updated self.form_input that includes 'role' (and optional
        'profile_picture'), the form should now be valid.
        """
        form = UserForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        """
        This tests username regex or uniqueness.
        If 'badusername' doesn't match '^@\\w{3,}$',
        it should fail validation.
        """
        self.form_input['username'] = 'badusername'  # Invalid based on your regex
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        """
        This test ensures updating an existing user from the fixture
        to the new data doesn't create new user; it updates the existing one.
        """
        user = User.objects.get(username='@johndoe')  # from fixture
        form = UserForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        saved_user = form.save()  # If form is valid, this updates the user
        after_count = User.objects.count()

        # We expect the count not to change since it's an update, not a create.
        self.assertEqual(after_count, before_count)
        self.assertEqual(saved_user.username, '@janedoe')
        self.assertEqual(saved_user.first_name, 'Jane')
        self.assertEqual(saved_user.last_name, 'Doe')
        self.assertEqual(saved_user.email, 'janedoe@example.org')