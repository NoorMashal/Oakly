from django.urls import path, include
from . import views
from .views import OakleyPasswordResetView
from django.contrib.auth import views as auth_views

app_name = 'Oakley'

urlpatterns = [
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path("", views.login_view, name="login"),
    path("home/", views.home, name="home"),
    path('transactions/import/', views.import_transactions, name='import_transactions'),
    path("transactions/", views.transactions, name="transactions"),
    path('budget-planning/', views.budget_planning, name='budget_planning'),
    path("signup/", views.signup_view, name="signup"),
    path("questionnaire/", views.questionnaire, name="questionnaire"),
    path("profile/", views.profile, name="profile"),
    path("reports/", views.reports, name="reports"),
    path("logout/", views.logout_view, name="logout"),
    path('transactions/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('advisor/signup/', views.advisor_signup, name='advisor_signup'),
    path('advisor/home/', views.advisor_meetings, name='advisor_home'),
    path('advisor/profile/', views.advisor_profile, name='advisor_profile'),
    path ('advisor/questionnaire/', views.advisor_questionnaire, name='advisor_questionnaire'),
    path('meetings/', views.meetings, name='meetings'),
    path('meetings/<int:meeting_id>/cancel/', views.cancel_meeting, name='cancel_meeting'),
    path('meetings/<int:meeting_id>/complete/', views.complete_meeting, name='complete_meeting'),
    path('advisor/meetings', views.advisor_meetings, name='advisor_meetings'),
    path('schedule/', views.schedule, name='schedule'),
    path('advisor/feedback/<int:meeting_id>/', views.give_feedback, name='give_feedback'),
    path('advisor/feedback/<int:meeting_id>/edit/', views.edit_feedback, name='edit_feedback'),
    path('advisor/dashboard/<int:user_id>/', views.advisor_view_user_dashboard, name='advisor_user_dashboard'),
    path('password_reset/', OakleyPasswordResetView.as_view(), name='password_reset'),
    path('accounts/', include('allauth.urls')),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='Oakley/registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='Oakley/registration/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='Oakley/registration/password_reset_complete.html'), name='password_reset_complete'),
]