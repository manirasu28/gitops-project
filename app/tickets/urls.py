from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='tickets/logout.html', next_page='home'), name='logout'),
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='tickets/password_reset.html', email_template_name='tickets/password_reset_email.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='tickets/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='tickets/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='tickets/password_reset_complete.html'), name='password_reset_complete'),
    
    # User profile
    path('profile/', views.profile, name='profile'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Tickets
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/list/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:ticket_id>/update-status/', views.update_ticket_status, name='update_ticket_status'),
    
    # Admin/Support FAQ Management
    path('manage-faq/', views.manage_faq, name='manage_faq'),
]
