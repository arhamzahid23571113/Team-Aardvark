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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Authentication and User Management
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    
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
    path('request_lesson/', views.request_lesson, name='request_lesson'),
    path('contact_admin/',views.contact_admin,name='contact_admin'),
    path('my_tutor_profile/',views.see_my_tutor,name='my_tutor_profile'),
    path('my_students_profile/',views.see_my_students_profile,name='my_students_profile'),
    path('request_success/', views.lesson_request_success, name='lesson_request_success'),
    path('student_requests/', views.student_requests, name='student_requests'),
    path('assign_tutor/<int:lesson_request_id>/', views.assign_tutor, name='assign_tutor'),
    path('unassign-tutor/<int:lesson_request_id>/', views.unassign_tutor, name='unassign_tutor'),
    path('cancel-request/<int:lesson_request_id>/', views.cancel_request, name='cancel_request'),
    path('tutor-profiles/', views.all_tutor_profiles, name='all_tutor_profiles'),
    path('tutor-profile/<int:tutor_id>/', views.view_tutor_profile, name='view_tutor_profile'),
    path('tutor-profile/<int:tutor_id>/edit/', views.edit_tutor_profile, name='edit_tutor_profile'),
    path('all-students/', views.all_student_profiles, name='all_students'),
    path('tutor/<int:tutor_id>/info/', views.tutor_more_info, name='tutor_more_info'),
    path('admin-messages/', views.admin_messages, name='admin_messages'),








    # New Pages
    path('learn-more/', views.learn_more, name='learn_more'),
    path('available-courses/', views.available_courses, name='available_courses'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
