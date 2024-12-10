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
     invalid_data = {
        'role': 'invalid_role',  
        'message': 'This is a test message.'
     }
     form = ContactMessages(data=invalid_data)
     self.assertFalse(form.is_valid())
     self.assertIn('role', form.errors) 

   

    def test_contact_messages_form_widgets(self):
     form = ContactMessages()
     self.assertEqual(
        form.fields['role'].widget.choices,
        [("student", "Student"), ("tutor", "Tutor")]
     )
     self.assertEqual(form.fields['message'].widget.attrs['rows'], 4)