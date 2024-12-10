from django.test import TestCase
from tutorials.forms import ContactMessages
from django import forms

class ContactMessagesFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'role': 'student',
            'message': 'This is a test message to the admin.'
        }

        self.invalid_data = {
            'role': 'invalid_role',
            'message': ''
        }

    def test_contact_messages_form_valid(self):
        form = ContactMessages(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['role'], self.valid_data['role'])
        self.assertEqual(form.cleaned_data['message'], self.valid_data['message'])

    def test_contact_messages_form_invalid(self):
        form = ContactMessages(data=self.invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)
        self.assertIn('message', form.errors)

    def test_contact_messages_form_widgets(self):
        form = ContactMessages()
        self.assertIsInstance(form.fields['message'].widget, forms.Textarea)
        self.assertEqual(form.fields['message'].widget.attrs['rows'], 4)
        self.assertIsInstance(form.fields['role'].widget, forms.Select)
        self.assertEqual(form.fields['role'].widget.choices, [
            ("student", "Student"),
            ("tutor", "Tutor"),
        ])