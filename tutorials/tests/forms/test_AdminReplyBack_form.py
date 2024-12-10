from django.test import TestCase
from tutorials.forms import AdminReplyBack
from tutorials.models import ContactMessage

class AdminReplyBackFormTest(TestCase):
    def setUp(self):
        self.valid_data = {'reply': 'Thank you for reaching out.'}
        self.empty_data = {'reply': ''}

    def test_form_is_valid_with_reply(self):
        form = AdminReplyBack(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_is_valid_with_empty_reply(self):
        form = AdminReplyBack(data=self.empty_data)
        self.assertTrue(form.is_valid())

    def test_form_has_correct_placeholder_in_widget(self):
        form = AdminReplyBack()
        self.assertIn('placeholder', form.fields['reply'].widget.attrs)
        self.assertEqual(form.fields['reply'].widget.attrs['placeholder'], 'Write response here')

    def test_form_has_correct_rows_attribute_in_widget(self):
        form = AdminReplyBack()
        self.assertIn('rows', form.fields['reply'].widget.attrs)
        self.assertEqual(form.fields['reply'].widget.attrs['rows'], 4)