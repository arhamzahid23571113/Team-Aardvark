"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from tutorials import views
from django.urls import path
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Authentication and User Management
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Role-Based Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tutor_dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('invoice_page/', views.invoice_page, name='invoice_page'),
    path('invoice_page/<str:term_name>/', views.invoice_page, name='invoice_page_term'),
    path('manage_invoices/', views.manage_invoices, name='manage_invoices'),
    path('admin_invoice_view/<str:invoice_num>/', views.admin_invoice_view, name='admin_invoice_view'), 
    path('request_lesson/', views.request_lesson, name='request_lesson'),
    path('contact_admin/',views.contact_admin,name='contact_admin'),
    path('my_tutor_profile/',views.see_my_tutor,name='my_tutor_profile'),
    path('my_students_profile/',views.see_my_students_profile,name='my_students_profile'),
    path('request_success/', views.lesson_request_success, name='lesson_request_success'),
    path('response_submitted/',views.response_submitted_success,name='response_success'),
    path('student_requests/', views.student_requests, name='student_requests'),
    path('assign_tutor/<int:lesson_request_id>/', views.assign_tutor, name='assign_tutor'),
    path('unassign_tutor/<int:lesson_request_id>/', views.unassign_tutor, name='unassign_tutor'),
    path('cancel_request/<int:lesson_request_id>/', views.cancel_request, name='cancel_request'),
    path('all_tutor_profiles/', views.all_tutor_profiles, name='all_tutor_profiles'),
    path('view_tutor_profile/<int:tutor_id>/', views.view_tutor_profile, name='view_tutor_profile'),
    path('edit_tutor_profile/<int:tutor_id>/edit/', views.edit_tutor_profile, name='edit_tutor_profile'),
    path('view_student_profile/<int:student_id>/',views.view_student_profile,name='view_student_profile'),
    path('all_students/', views.all_student_profiles, name='all_students'),
    path('tutor/<int:tutor_id>/info/', views.tutor_more_info, name='tutor_more_info'),
    path('admin_messages/<str:role>/', views.admin_messages, name='admin_messages'),
    path('contact_admin_form_page/',views.send_message_to_admin,name='send_message_to_admin'),
    path('view_student_messages/<str:role>/',views.view_student_messages,name='view_student_messages'),
    path('view_tutor_messages/<str:role>/',views.view_tutor_messages,name='view_tutor_messages'),
    path('admin_reply/<int:message_id>/', views.admin_reply, name='admin_reply'),
    path('tutor_messages/', views.tutor_messages, name='tutor_messages'),
    path('student_messages/', views.student_messages, name='student_messages'),
    path('tutor/my_profile/', views.tutor_profile, name='tutor_profile'),
    path('tutor/edit_profile/', views.edit_profile, name='edit_profile'),
    path('student/my_profile/', views.student_profile, name='student_profile'),
    path('admin/my_profile/', views.admin_profile, name='admin_profile'),

    # New Pages
    path('learn-more/', views.learn_more, name='learn_more'),
    path('available-courses/', views.available_courses, name='available_courses'),
    #AMINA
    path('tutor/timetable/', views.see_my_tutor_timetable, name='tutor_timetable'),
    path('student/timetable/', views.see_my_student_timetable, name='student_timetable'), 
    
    
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
