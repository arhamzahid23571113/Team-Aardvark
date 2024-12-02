from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from .models import User
from .models import LessonRequest
from django.shortcuts import get_object_or_404, redirect
from .forms import LessonBookingForm



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


@login_required
def admin_dashboard(request):
    """Admin-specific dashboard."""
    return render(request, 'admin_dashboard.html')


@login_required
def tutor_dashboard(request):
    """Tutor-specific dashboard."""
    return render(request, 'tutor_dashboard.html')


@login_required
def student_dashboard(request):
    """Student-specific dashboard."""
    return render(request, 'student_dashboard.html')


def learn_more(request):
    """Display the Learn More page."""
    return render(request, 'learn_more.html')


def available_courses(request):
    """Display the Available Courses page."""
    return render(request, 'available_courses.html')


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
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
     """Display user profile editing screen and handle profile modifications."""

     model = User
     template_name = "profile.html"
     form_class = UserForm

     def get_object(self):
        return self.request.user

     def get_success_url(self):
        messages.success(self.request, "Profile updated!")
        return reverse('dashboard')

     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Determine the base template based on the user's role
        if hasattr(self.request.user, 'role'):  # Ensure the role attribute exists
            if self.request.user.role == 'tutor':
                profile_base_template = 'dashboard_base_tutor.html'
            elif self.request.user.role == 'student':
                profile_base_template = 'dashboard_base_student.html'
            elif self.request.user.role == 'admin':
                profile_base_template = 'dashboard_base_admin.html'
            else:
                profile_base_template = 'dashboard.html'  # Default for other roles
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
        return reverse('dashboard')

@login_required
def admin_dashboard(request):
    """Admin-specific dashboard."""
    return render(request, 'admin_dashboard.html')

@login_required
def tutor_dashboard(request):
    """Tutor-specific dashboard."""
    return render(request, 'tutor_dashboard.html')


@login_required
def student_dashboard(request):
    """Student-specific dashboard."""
    return render(request, 'student_dashboard.html')



@login_required
def request_lesson(request):
    if request.method == 'POST':
        form = LessonBookingForm(request.POST)
        if form.is_valid():
            lesson_request = form.save(commit=False)
            lesson_request.student = request.user  # Associate with the logged-in user
            lesson_request.save()
            return redirect('lesson_request_success')  # Redirect to a success page
        else:
            # Debugging form errors if needed
            print(form.errors)
    else:
        form = LessonBookingForm()

    return render(request, 'request_lesson.html', {'form': form})

@login_required
def contact_admin(request):
        # Determine the base template based on the user's role
    if request.user.is_authenticated:
        if request.user.role == 'tutor':
            base_template = 'dashboard_base_tutor.html'
        elif request.user.role == 'student':
            base_template = 'dashboard_base_student.html'
        elif request.user.role == 'admin':
            base_template = 'dashboard_base_admin.html'
        else:
            base_template = 'dashboard.html'  # Default for other roles
    else:
        base_template = 'dashboard.html'  # Default for unauthenticated users

    
    return render(request, 'contact_admin.html', {'base_template': base_template})



@login_required
def see_my_tutor_profile(request):
    return render(request,'my_tutor_profile.html')

@login_required
def see_my_students_profile(request):
 # Ensure only tutors can access this page
    if request.user.role != 'tutor':
        return redirect('dashboard')

    # Fetch all unique students assigned to the current tutor
    assigned_students = (
        User.objects.filter(
            lesson_requests__tutor=request.user  # Filter users linked to lesson requests for this tutor
        )
        .distinct()
    )

    context = {
        'students': assigned_students,
    }
    return render(request, 'my_students_profile.html', context)

@login_required
def lesson_request_success(request):
    return render(request, 'lesson_request_success.html')

@login_required
def student_requests(request):
    lesson_requests = LessonRequest.objects.select_related('student').order_by('student')

    # Group requests by student
    students_with_requests = {}
    for req in lesson_requests:
        if req.student not in students_with_requests:
            students_with_requests[req.student] = []
        students_with_requests[req.student].append(req)

    tutors = User.objects.filter(role='tutor')  # Fetch all tutors

    context = {
        'students_with_requests': students_with_requests,
        'tutors': tutors,
    }
    return render(request, 'student_requests.html', context)


@login_required
def assign_tutor(request, lesson_request_id):
    if request.method == 'POST':
        # Fetch the lesson request and selected tutor
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
        tutor_id = request.POST.get('tutor_id')

        if tutor_id:
            tutor = get_object_or_404(User, id=tutor_id, role='tutor')
            # Assign the tutor to the lesson request (assuming you have a 'tutor' field)
            lesson_request.tutor = tutor
            lesson_request.status = 'Allocated'
            lesson_request.save()

        return redirect('student_requests')  # Redirect back to the requests page
    
@login_required
def unassign_tutor(request, lesson_request_id):
    if request.method == 'POST':
        # Fetch the lesson request
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)

        # Unassign the tutor and update the status
        lesson_request.tutor = None
        lesson_request.status = 'Unallocated'
        lesson_request.save()

        # Redirect back to the student requests page
        return redirect('student_requests')
    
@login_required
def cancel_request(request, lesson_request_id):
    if request.method == 'POST':
        # Fetch the lesson request
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
        # Update the status to 'Cancelled'
        lesson_request.status = 'Cancelled'
        lesson_request.tutor = None  # Unassign the tutor
        lesson_request.save()
        # Redirect back to the student requests page
        return redirect('student_requests')

@login_required
def all_tutor_profiles(request):
    # Fetch all tutors (users with role='tutor') FOR ADMIN
    tutors = User.objects.filter(role='tutor')
    context = {'tutors': tutors}
    return render(request, 'all_tutor_profiles.html', context)

@login_required
def all_student_profiles(request):
    # Fetch all student (users with role='student') FOR ADMIN
    tutors = User.objects.filter(role='student')
    context = {'tutors': tutors}
    return render(request, 'all_student_profiles.html', context)

@login_required
def view_tutor_profile(request, tutor_id):
    # Fetch a specific tutor by ID
    tutor = get_object_or_404(User, id=tutor_id, role='tutor')
    return render(request, 'view_tutor_profile.html', {'tutor': tutor})

@login_required
def edit_tutor_profile(request, tutor_id):
    # Fetch a specific tutor by ID
    tutor = get_object_or_404(User, id=tutor_id, role='tutor')
    if request.method == 'POST':
        # Handle the form submission for editing tutor details (e.g., expertise)
        tutor.expertise = request.POST.get('expertise', tutor.expertise)
        tutor.save()
        return redirect('all_tutor_profiles')
    return render(request, 'edit_tutor_profile.html', {'tutor': tutor})
    