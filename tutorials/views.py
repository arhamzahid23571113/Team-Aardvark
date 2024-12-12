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
from datetime import date
from .models import User, LessonBooking, Invoice
from .models import LessonRequest
from django.shortcuts import get_object_or_404, redirect
from .forms import LessonBookingForm



#@login_required
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


#@login_prohibited
def home(request):
    """Display the application's start/home screen."""
    return render(request, 'home.html')


#@login_required
def admin_dashboard(request):
    """Admin-specific dashboard."""
    return render(request, 'admin_dashboard.html')


#@login_required
def tutor_dashboard(request):
    """Tutor-specific dashboard."""
    return render(request, 'tutor_dashboard.html')


#@login_required
def student_dashboard(request):
    """Student-specific dashboard."""
    '''student = request.user  
    invoices = Invoice.objects.filter(student=student)
    return render(request, 'student_dashboard.html', {'invoices': invoices})'''
    return render(request, 'student_dashboard.html')

def learn_more(request):
    """Display the Learn More page."""
    return render(request, 'learn_more.html')


def available_courses(request):
    """Display the Available Courses page."""
    return render(request, 'available_courses.html')

#@login_required
def manage_invoices(request):
    
    return render(request, 'manage_invoices.html')
    

#@login_required
def invoice_page(request, invoice_id, term_name = None):
    """Display user invoice."""
    invoice = Invoice.objects.get(id=invoice_id)

    total = 0

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
    
    lesson_requests = LessonRequest.objects.filter(student=invoice.student, request_date__range=[term_start, term_end], status='Allocated')

    term_keys = list(terms.keys())
    current_term_index = term_keys.index(term_name)

    previous_term = term_keys[(current_term_index - 1) % len(term_keys)]
    next_term = term_keys[(current_term_index + 1) % len(term_keys)]

    for booking in lesson_requests:
        booking.lesson_price = (booking.requested_duration / 60) * settings.HOURLY_RATE
        total += booking.lesson_price 

        booking.standardised_date = booking.request_date.strftime("%d/%m/%Y")

    return render(request, 'invoice_page.html', {
        'invoice': invoice, 
        'lesson_requests': lesson_requests,
        'total': total, 
        'term_name': term_name.title(),
        'previous_term': previous_term,
        'next_term': next_term,
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

#@login_required
def admin_dashboard(request):
    """Admin-specific dashboard."""
    return render(request, 'admin_dashboard.html')

#@login_required
def tutor_dashboard(request):
    """Tutor-specific dashboard."""
    return render(request, 'tutor_dashboard.html')


#@login_required
def student_dashboard(request):
    """Student-specific dashboard."""
    return render(request, 'student_dashboard.html')


#STUDENTS
#@login_required
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

#STUDENT OR TUTOR
#@login_required
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


#STUDENTS
#@login_required
def see_my_tutor(request):
    # Ensure only students can access this page
    if request.user.role != 'student':
        return redirect('dashboard')

    # Fetch the tutor assigned to the logged-in student via LessonRequest
    assigned_tutors = LessonRequest.objects.filter(
        student=request.user,  # Filter by the logged-in student
        tutor__isnull=False,   # Ensure a tutor is assigned
        status='Allocated'     # Optional: Only show allocated tutors
    ).values(
        'tutor__id',
        'tutor__first_name',
        'tutor__last_name',
        'tutor__email',
        'tutor__expertise'
    ).distinct()

    context = {
        'tutors': assigned_tutors,  # Pass the tutors to the template
    }

    return render(request, 'my_tutor_profile.html', context)

#TUTORS
#@login_required
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


#STUDENTS
#@login_required
def lesson_request_success(request):
    return render(request, 'lesson_request_success.html')


#ADMINS
def student_requests(request):
#@login_required
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



#ADMINS
#@login_required
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
    

#ADMINS
#@login_required
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
    

#ADMINS
#@login_required
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


#ADMINS
#@login_required
def all_tutor_profiles(request):
    # Fetch all tutors (users with role='tutor') 
    tutors = User.objects.filter(role='tutor')
    context = {'tutors': tutors}
    return render(request, 'all_tutor_profiles.html', context)

#ADMINS
#@login_required
def all_student_profiles(request):
    # Fetch all students (users with role='student') 
    students = User.objects.filter(role='student')
    context = {'students': students}
    return render(request, 'all_student_profiles.html', context)


#ADMINS
#@login_required
def view_tutor_profile(request, tutor_id):
    # Fetch a specific tutor by ID 
    tutor = get_object_or_404(User, id=tutor_id, role='tutor')
    return render(request, 'view_tutor_profile.html', {'tutor': tutor})


#ADMINS
#@login_required
def edit_tutor_profile(request, tutor_id):
    # Fetch a specific tutor by ID 
    tutor = get_object_or_404(User, id=tutor_id, role='tutor')
    if request.method == 'POST':
        # Handle the form submission for editing tutor details (e.g., expertise)
        tutor.expertise = request.POST.get('expertise', tutor.expertise)
        tutor.save()
        return redirect('all_tutor_profiles')
    return render(request, 'edit_tutor_profile.html', {'tutor': tutor})
    

  #STUDENTS
#@login_required
def tutor_more_info(request, tutor_id):
    # Ensure only students can access this page 
    if request.user.role != 'student':
        return redirect('dashboard')

    # Get the tutor's details
    tutor = get_object_or_404(User, id=tutor_id, role='tutor')

    # Get the lesson requests where the logged-in student is linked to the tutor
    lessons = LessonRequest.objects.filter(student=request.user, tutor=tutor)

    context = {
        'tutor': tutor,
        'lessons': lessons,
    }

    return render(request, 'tutor_more_info.html', context)
