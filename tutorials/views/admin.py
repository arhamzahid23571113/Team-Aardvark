from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.shortcuts import render
from django.shortcuts import render
from tutorials.models import User, Invoice

from tutorials.models import LessonRequest
from django.shortcuts import get_object_or_404, redirect
from tutorials.models import ContactMessage
from tutorials.forms import AdminReplyBack
from django.utils.timezone import now
from django.http import HttpResponseForbidden

from .common import generate_invoice

@login_required
def admin_dashboard(request):
    """Admin-specific dashboard."""
    return render(request, 'admin_dashboard.html')

@login_required
def admin_invoice_view(request, invoice_num):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")

    invoice = get_object_or_404(Invoice, invoice_num=invoice_num)

    lesson_requests, total = generate_invoice(invoice)

    for booking in lesson_requests:
        booking.standardised_date = booking.request_date.strftime("%d/%m/%Y")
        if hasattr(booking, 'requested_topic'):
            del booking.requested_topic

    base_template = 'dashboard_base_admin.html' if request.user.role == 'admin' else 'dashboard_base_student.html'

    return render(request, 'invoice_page.html', {
        'invoice': invoice,
        'lesson_requests': lesson_requests,
        'total': total,
        'is_admin': True,  
        'base_template' : base_template,
    })

@login_required
def assign_tutor(request, lesson_request_id):
    if request.method == 'POST':
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
        tutor_id = request.POST.get('tutor_id')

        if tutor_id:
            tutor = get_object_or_404(User, id=tutor_id, role='tutor')
            lesson_request.tutor = tutor
            lesson_request.status = 'Allocated'
            lesson_request.save()

        return redirect('student_requests') 
    
@login_required
def unassign_tutor(request, lesson_request_id):
    if request.method == 'POST':
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
        lesson_request.tutor = None
        lesson_request.status = 'Unallocated'
        lesson_request.save()
        return redirect('student_requests')

@login_required
def cancel_request(request, lesson_request_id):
    if request.method == 'POST':
        lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
        lesson_request.status = 'Cancelled'
        lesson_request.tutor = None  
        lesson_request.save()
        return redirect('student_requests')

@login_required
def all_tutor_profiles(request):
    tutors = User.objects.filter(role='tutor')
    context = {'tutors': tutors}
    return render(request, 'all_tutor_profiles.html', context)

@login_required
def all_student_profiles(request):
    students = User.objects.filter(role='student')
    context = {'students': students}
    return render(request, 'all_student_profiles.html', context)

@login_required
def view_tutor_profile(request, tutor_id):
    tutor = get_object_or_404(User, id=tutor_id, role='tutor')
    return render(request, 'view_tutor_profile.html', {'tutor': tutor})

@login_required
def admin_messages(request,role=None):
    role = role or request.GET.get('role')
    if role == "all":
        messages = ContactMessage.objects.all().order_by('-timestamp')
    elif role in ['student','tutor']:
        messages = ContactMessage.objects.filter(role=role).order_by('-timestamp')
    else:
        messages = []
    return render(request, 'admin_messages.html', {'messages': messages, 'role_filter': role})

@login_required
def view_student_messages(request,role=None):
    if request.user.role == 'admin':
        student_messages = ContactMessage.objects.filter(role='student').order_by('timestamp')
        return render(request,'admin_messages_students.html',{'messages':student_messages})
    else:
        return redirect('log_in')

@login_required
def view_tutor_messages(request,role=None):
    if request.user.role == 'admin':
        tutor_messages = ContactMessage.objects.filter(role='tutor').order_by('timestamp')
        return render(request,'admin_messages_tutors.html',{'messages':tutor_messages})
    else:
        return redirect('log_in')
    
def admin_reply(request, message_id):
    if request.user.role != 'admin':  
        return redirect('log_in')

    message = get_object_or_404(ContactMessage, id=message_id)

    if request.method == 'POST':
        adminForm = AdminReplyBack(request.POST, instance=message)
        if adminForm.is_valid():
            reply_message = adminForm.save(commit=False)
            reply_message.reply_timestamp = now()  
            reply_message.save()
            messages.success(request, f"Reply successfully sent to {message.user.first_name}!")
            return redirect('response_success')
        else:
            messages.error(request, "There was an error with your reply, it has not been saved successfully.")
    else:
        adminForm = AdminReplyBack(instance=message)

    return render(request, 'admin_reply.html', {'form': adminForm, 'message': message})

@login_required
def student_requests(request):
    if request.user.role != 'admin':  
        return redirect('log_in')  
    lesson_requests = LessonRequest.objects.select_related('student').order_by('student')
    students_with_requests = {}
    for req in lesson_requests:
        if req.student not in students_with_requests:
            students_with_requests[req.student] = []
        students_with_requests[req.student].append(req)

    tutors = User.objects.filter(role='tutor')  

    context = {
        'students_with_requests': students_with_requests,
        'tutors': tutors,
    }
    return render(request, 'student_requests.html', context)

@login_required
def admin_profile(request):
    """Display the admin's profile."""
    if request.user.role != 'admin':
        messages.error(request, "Access denied. Only admins can view this page.")
        return redirect('dashboard')

    admin = request.user

    context = {
        'admin': admin,
    }
    return render(request, 'admin_profile.html', context)

@login_required
def manage_invoices(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")

    invoices = Invoice.objects.filter(payment_status='Unpaid')
    invoice_data = []

    for invoice in invoices:
        lesson_requests, total = generate_invoice(invoice)
        invoice.standardised_due_date = invoice.due_date.strftime("%d/%m/%Y")

        invoice_data.append({
            'invoice' : invoice,
            'lesson_requests' : lesson_requests,
            'total' : total,
        })

    return render(request, 'manage_invoices.html', {'invoice_data' : invoice_data})


