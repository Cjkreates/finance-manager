from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import reset_admin_password  # Good to keep import at the top

urlpatterns = [

    

    path('income/edit/<int:pk>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:pk>/', views.delete_income, name='delete_income'),
    path('expense/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),

    path('income/cbv/edit/<int:pk>/', views.IncomeUpdateView.as_view(), name='cbv_edit_income'),
    path('income/cbv/delete/<int:pk>/', views.IncomeDeleteView.as_view(), name='cbv_delete_income'),



    path("create-admin/", views.create_admin_user, name="create_admin"),  # Only one needed

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
