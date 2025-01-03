from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.urls import reverse
from datetime import date
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from datetime import timedelta, date
from django.shortcuts import render
from datetime import timedelta
from tutorials.models import User, Invoice, LessonRequest, Lesson
from tutorials.forms import ContactMessages
from django.shortcuts import redirect
from django.http import HttpResponse
import logging

@login_required
def dashboard(request):
    """Redirect users to their role-based dashboards."""
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'tutor':
        return redirect('tutor_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    else:
        messages.error(request, "Invalid user role!")
        return redirect('home')

@login_prohibited
def home(request):
    """Display the application's start/home screen."""
    return render(request, 'home.html')

def learn_more(request):
    """Display the Learn More page."""
    return render(request, 'learn_more.html')

def available_courses(request):
    """Display the Available Courses page."""
    return render(request, 'available_courses.html')

def generate_invoice(invoice, term_start=None, term_end=None):
    total = 0

    if term_start and term_end:
        lesson_requests = LessonRequest.objects.filter(
            student=invoice.student, 
            requested_date__range=[term_start, term_end], 
            status='Allocated')
    else:
        lesson_requests = LessonRequest.objects.filter(
            student=invoice.student, 
            status='Allocated')

    for booking in lesson_requests:
        booking.lesson_price = (booking.requested_duration / 60) * settings.HOURLY_RATE
        total += booking.lesson_price 

    if total == 0:
        invoice.payment_status = 'Paid' 
    else:
        invoice.payment_status = 'Unpaid'

    invoice.save()

    return lesson_requests, total


@login_required
def invoice_page(request, term_name = None):
    """Display user invoice."""
    terms = {
        'autumn': (date(2024, 9, 1), date(2024, 12, 31)),
        'spring': (date(2025, 1, 1), date (2025, 5, 31)),
        'summer': (date(2025, 6, 1), date(2025, 8, 31)),
    }

    if term_name is None:
        today = date.today()

        for term, (start, end) in terms.items():
            if start <= today <= end:
                term_name = term 
                break 

    term_dates = terms.get(term_name)
    term_start, term_end = term_dates

    invoice = Invoice.objects.filter(student=request.user).first()

    if not invoice:
        return HttpResponse("No invoice found", status=404)    

    term_keys = list(terms.keys())
    current_term_index = term_keys.index(term_name)

    previous_term = term_keys[(current_term_index - 1) % len(term_keys)]
    next_term = term_keys[(current_term_index + 1) % len(term_keys)]

    lesson_requests, total = generate_invoice(invoice, term_start, term_end)

    for booking in lesson_requests:
        booking.standardised_date = booking.request_date.strftime("%d/%m/%Y")

    base_template = 'dashboard_base_admin.html' if request.user.role == 'admin' else 'dashboard_base_student.html'

    return render(request, 'invoice_page.html', {
        'invoice': invoice, 
        'lesson_requests': lesson_requests,
        'total': total, 
        'term_name': term_name.title(),
        'previous_term': previous_term,
        'next_term': next_term,
        'base_template' : base_template,
        })

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        return self.redirect_when_logged_in_url

class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user:
            login(request, user)
            return redirect(self.next)
        messages.error(request, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})

def log_out(request):
    """Log out the current user."""
    logout(request)
    return redirect('home')

class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Password updated!")
        return reverse('log_in')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen and handle profile modifications."""

    model = User
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profile updated successfully!")
        return response

    def get_success_url(self):
        return reverse('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if hasattr(self.request.user, 'role'):  
            if self.request.user.role == 'tutor':
                profile_base_template = 'dashboard_base_tutor.html'
            elif self.request.user.role == 'student':
                profile_base_template = 'dashboard_base_student.html'
            elif self.request.user.role == 'admin':
                profile_base_template = 'dashboard_base_admin.html'
            else:
                profile_base_template = 'dashboard.html'  
        else:
            profile_base_template = 'dashboard.html'

        context['profile_base_template'] = profile_base_template
        return context

class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('log_in')

logger = logging.getLogger(__name__)

@login_required
def contact_admin(request):
    if request.user.is_authenticated:
        if request.user.role == 'tutor':
            base_template = 'dashboard_base_tutor.html'
        elif request.user.role == 'student':
            base_template = 'dashboard_base_student.html'
        elif request.user.role == 'admin':
            base_template = 'dashboard_base_admin.html'
        else:
            base_template = 'dashboard.html'  
    else:
        base_template = 'dashboard.html'  
    return render(request, 'contact_admin.html', {'base_template': base_template})

def generate_lessons(lesson_request, num_lessons=10):
    """
    Generate individual lessons from a lesson request.
    - lesson_request: The LessonRequest instance.
    - num_lessons: Number of lessons to generate (default 10).
    """
    start_date = lesson_request.requested_date
    frequency = 7 if lesson_request.requested_frequency == "weekly" else 14
    duration = lesson_request.requested_duration

    lessons = []
    for i in range(num_lessons):  
        lesson_date = start_date + timedelta(days=frequency * i)
        lesson = Lesson.objects.create(
            tutor=lesson_request.tutor,
            student=lesson_request.student,
            date=lesson_date,
            time=lesson_request.requested_time,
            duration=duration,
            topic=lesson_request.requested_topic
        )
        lessons.append(lesson)
    return lessons

@login_required
def lesson_request_success(request):
    dashboard_url = reverse('log_in')
    if request.user.is_authenticated:
        if request.user.role == 'tutor':
            base_template = 'dashboard_base_tutor.html'
            dashboard_url = reverse('tutor_dashboard')
        elif request.user.role == 'student':
            base_template = 'dashboard_base_student.html'
            dashboard_url = reverse('student_dashboard')
        elif request.user.role == 'admin':
            base_template = 'dashboard_base_admin.html'
            dashboard_url = reverse('admin_dashboard')
        else:
            base_template = 'dashboard.html'
    else:
        base_template = 'dashboard.html'
    return render(request, 'lesson_request_success.html',{'base_template':base_template,'dashboard_url':dashboard_url})

@login_required
def send_message_to_admin(request):
    if request.user.is_authenticated:
        if request.user.role == 'tutor':
            base_template = 'dashboard_base_tutor.html'
        elif request.user.role == 'student':
            base_template = 'dashboard_base_student.html'
        elif request.user.role == 'admin':
            base_template = 'dashboard_base_admin.html'
        else:
            base_template = 'dashboard.html'
    else:
        base_template = 'dashboard.html'

    if request.method == 'POST':
        form = ContactMessages(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.user = request.user  
            contact_message.save()
            messages.success(request, 'Your message has been submitted successfully!')
            return redirect('response_success')
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
        form = ContactMessages()

    return render(request, 'contact_admin.html', {'form': form, 'base_template': base_template})

@login_required
def response_submitted_success(request):
    dashboard_url = reverse('log_in')
    if request.user.is_authenticated:
        if request.user.role == 'tutor':
            base_template = 'dashboard_base_tutor.html'
            dashboard_url = reverse('tutor_dashboard')
        elif request.user.role == 'student':
            base_template = 'dashboard_base_student.html'
            dashboard_url = reverse('student_dashboard')
        elif request.user.role == 'admin':
            base_template = 'dashboard_base_admin.html'
            dashboard_url = reverse('admin_dashboard')
        else:
            base_template = 'home.html'
    else:
        base_template = 'home.html'
    return render(request, 'response_submitted.html',{'base_template':base_template,'dashboard_url':dashboard_url})

@login_required
def edit_profile(request):
    """Allow users to edit their profile details based on their role."""
    user = request.user

    role_templates = {
        'tutor': 'edit_my_tutor_profile.html',
        'student': 'edit_my_student_profile.html',
        'admin': 'edit_my_admin_profile.html'
    }
    profile_base_templates = {
        'tutor': 'dashboard_base_tutor.html',
        'student': 'dashboard_base_student.html',
        'admin': 'dashboard_base_admin.html'
    }

    if request.method == "POST":

        form = UserForm(request.POST, request.FILES, instance=user, user=user)
        if form.is_valid():

            updated_user = form.save(commit=False)
            if user.role == 'tutor':
                updated_user.expertise = form.cleaned_data.get('expertise')
            if 'profile_picture' in request.FILES:
                updated_user.profile_picture = request.FILES['profile_picture']
            updated_user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect(f"{user.role}_dashboard")
    else:
        form = UserForm(instance=user, user=user)

    return render(request, role_templates.get(user.role, 'dashboard.html'), {
        'form': form,
        'profile_base_template': profile_base_templates.get(user.role, 'dashboard.html'),
    })
    