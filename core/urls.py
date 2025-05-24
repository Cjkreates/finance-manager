from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import reset_admin_password  # Move this import to the top

urlpatterns = [
    path("create-admin/", views.create_admin_user, name="create_admin"),

    path("create-admin/", views.create_admin_user),

    path("reset-admin-password/", reset_admin_password, name='reset_admin_password'),

    path('', views.home, name='home'),  # Homepage or redirect to dashboard if logged in

    # Income URLs
    path('incomes/', views.income_list, name='income_list'),
    path('add-income/', views.add_income, name='add_income'),

    # Expense URLs
    path('expenses/', views.expense_list, name='expense_list'),
    path('add-expense/', views.add_expense, name='add_expense'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
