from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Admin Utilities
    path('create-admin/', views.create_admin_user, name='create_admin'),
    path('reset-admin-password/', views.reset_admin_password, name='reset_admin_password'),

    # Income Views
    path('incomes/', views.income_list, name='income_list'),
    path('add-income/', views.add_income, name='add_income'),
    path('income/edit/<int:pk>/', views.IncomeUpdateView.as_view(), name='edit_income'),
    path('income/delete/<int:pk>/', views.IncomeDeleteView.as_view(), name='delete_income'),

    # Expense Views
    path('expenses/', views.expense_list, name='expense_list'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('expense/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
]
