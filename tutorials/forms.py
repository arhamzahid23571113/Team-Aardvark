"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, LessonRequest,ContactMessage

from .models import User, LessonRequest,ContactMessage



class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""
        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'profile_picture', 'expertise']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role == 'tutor':
            self.fields.pop('role')  # Remove the role field for tutors

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        if not self.is_valid():
            raise ValueError("The form contains invalid data.")
        return super().save(commit=commit)

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase character, and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self.user = user
        if not user:
            raise ValueError("A valid user must be provided.")

    def clean(self):
        super().clean()
        password = self.cleaned_data.get('password')
        if self.user and not authenticate(username=self.user.username, password=password):
            self.add_error('password', "Password is invalid")

    def save(self):
        new_password = self.cleaned_data['new_password']
        if self.user:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']

    def save(self, commit=True):
        if not self.is_valid():
            raise ValueError("The form contains invalid data.")
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            role=self.cleaned_data.get('role'),
        )

        if commit:
            user.save()
        return user


class LessonBookingForm(forms.ModelForm):
    class Meta:
        model = LessonRequest
        fields = [
            "requested_topic",
            "requested_frequency",
            "requested_duration",
            "requested_time",
            "preferred_day",
            "experience_level",
            "additional_notes",
        ]
        widgets = {
            "requested_topic": forms.Select(choices=[
                ("python_programming", "Python Programming"),
                ("web_development_with_js", "Web Development with JavaScript"),
                ("ruby_on_rails", "Ruby on Rails"),
                ("ai_and_ml", "AI and Machine Learning"),
            ]),
            "requested_duration": forms.Select(choices=[
                ("30", "30 Minutes"),
                ("60", "1 Hour"),
                ("90", "1 Hour and 30 Minutes"),
                ("120", "2 Hours"),
            ]),
            "requested_frequency": forms.Select(choices=[
                ("weekly", "Weekly"),
                ("fortnightly", "Fortnightly"),
            ]),
            "preferred_day": forms.Select(choices=[
                ("monday", "Monday"),
                ("tuesday", "Tuesday"),
                ("wednesday", "Wednesday"),
                ("thursday", "Thursday"),
                ("friday", "Friday"),
                ("saturday", "Saturday"),
                ("sunday", "Sunday"),
            ]),
            "experience_level": forms.Select(choices=[
                ("no_experience", "No Experience"),
                ("beginner", "Beginner"),
                ("intermediate", "Intermediate"),
                ("advanced", "Advanced"),
            ]),
        }
        
#class ContactMessages(forms.ModelForm):
 #   class Meta:
  #      model = ContactMessage
  #      fields = ['role','message']
  #      exclude = ['timestamp']
   #     widgets = {
   #         'message': forms.Textarea(attrs={'rows':4}),
   #         'role': forms.Select(choices=[
    #            ("student","Student"),
    #            ("tutor","Tutor"),
     #       ])
     #   }
class ContactMessages(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['role', 'message']
        exclude = ['timestamp']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].widget = forms.Select(choices=[
            ("student", "Student"),
            ("tutor", "Tutor"),
        ])
        
class AdminReplyBack(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['reply']
        Widgets = {
            'reply': forms.Textarea(attrs={'row':4, 'placeholder': 'Write response here'}),
        }       