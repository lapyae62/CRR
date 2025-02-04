"""
Definition of urls for CRR.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from django.urls import path
from app import views


urlpatterns = [
    path('', views.home, name='home'),  # index.html
    path('about/', views.about, name='about'),  # about.html
    path('contact/', views.contact, name='contact'),  # contact.html
    path('assign_report_form/<int:report_id>/', views.assign_report_form, name='assign_report_form'),
    path('regional_reports/', views.regional_reports_view, name='regional_reports'),
    path('update_status_request/', views.update_status_request, name='update_status_request'),
    path('update_case/<int:case_id>/', views.update_case, name='update_case'),
    path('manage_assigned_cases/', views.manage_assigned_cases, name='manage_assigned_cases'),
    path('take_case/', views.take_case, name='take_case'),
    path('update_case/<int:report_id>/',views.update_case, name='update_case'),
    path('view-assigned-reports/', views.view_assigned_reports, name='view_assigned_reports'),
    path('report_crime/', views.report_crime, name='report_crime'),
    path('admin_reports/', views.admin_reports, name='admin_reports'),
    path('admin_users/', views.admin_users, name='admin_users'),
    path('add_user/', views.add_user, name='add_user'),
    path('process_feedback/', views.process_feedback, name='process_feedback'),
    path('process_feedback/', views.manage_requests, name='manage_requests'),
    path('process_rank_request/', views.process_rank_request, name='process_rank_request'),
    path('process_region_request/', views.process_region_request, name='process_region_request'),
    path('custom_login/' ,views.custom_login, name='custom_login'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
]


