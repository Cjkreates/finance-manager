from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib import messages
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from .models import Income, Expense
from .forms import Incomeform, Expenseform, RegisterForm

# Admin credentials from settings
ADMIN_USERNAME = getattr(settings, "ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = settings.ADMIN_PASSWORD
SECRET_RESET_PASSWORD = settings.SECRET_RESET_PASSWORD

# Restrict admin operations to staff users
def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

@staff_required
def create_admin_user(request):
    if User.objects.filter(username=ADMIN_USERNAME).exists():
        return HttpResponse("Admin user already exists.")
    User.objects.create_superuser(username=ADMIN_USERNAME, email="", password=ADMIN_PASSWORD)
    return HttpResponse("Admin user created successfully.")

@staff_required
def reset_admin_password(request):
    if request.method != 'POST' or request.POST.get("secret") != SECRET_RESET_PASSWORD:
        return HttpResponse("Not authorized", status=403)
    user = get_object_or_404(User, username=ADMIN_USERNAME)
    user.set_password(SECRET_RESET_PASSWORD)
    user.save()
    return HttpResponse("Password reset successful.")

# Home view
def home(request):
    return render(request, 'core/home.html')

# Dashboard view
@login_required
def dashboard(request):
    user = request.user
    total_income = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    expense_data = Expense.objects.filter(user=user).values('category').annotate(total=Sum('amount'))
    monthly_income = Income.objects.filter(user=user).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
    monthly_expense = Expense.objects.filter(user=user).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')

    expense_categories = [item['category'] for item in expense_data]
    expense_totals = [float(item['total']) for item in expense_data]

    months = sorted(set(
        [item['month'].strftime('%b %Y') for item in monthly_income] +
        [item['month'].strftime('%b %Y') for item in monthly_expense]
    ))

    income_totals = [
        float(next((item['total'] for item in monthly_income if item['month'].strftime('%b %Y') == month), 0))
        for month in months
    ]
    expense_totals_monthly = [
        float(next((item['total'] for item in monthly_expense if item['month'].strftime('%b %Y') == month), 0))
        for month in months
    ]

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'expense_categories': expense_categories,
        'expense_totals': expense_totals,
        'months': months,
        'income_totals': income_totals,
        'expense_totals_monthly': expense_totals_monthly,
    }
    return render(request, 'core/dashboard.html', context)

# User registration
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')

    return render(request, 'core/register.html', {'form': form})

# Income views
@login_required
def income_list(request):
    query = request.GET.get('q', '')
    incomes = Income.objects.filter(user=request.user)
    if query:
        incomes = incomes.filter(
            Q(source__icontains=query) |
            Q(description__icontains=query) |
            Q(amount__icontains=query)
        )
    paginator = Paginator(incomes, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/income_list.html', {'page_obj': page_obj})

@login_required
def add_income(request):
    form = Incomeform(request.POST or None)
    if form.is_valid():
        income_entry = form.save(commit=False)
        income_entry.user = request.user
        income_entry.save()
        messages.success(request, "Income added successfully.")
        return redirect('income_list')
    return render(request, 'core/add_income.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class IncomeUpdateView(UpdateView):
    model = Income
    form_class = Incomeform
    template_name = 'core/edit_income.html'
    success_url = reverse_lazy('income_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

@method_decorator(login_required, name='dispatch')
class IncomeDeleteView(DeleteView):
    model = Income
    template_name = 'core/delete_confirm.html'
    success_url = reverse_lazy('income_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

# Expense views
@login_required
def expense_list(request):
    query = request.GET.get('q', '')
    expenses = Expense.objects.filter(user=request.user)
    if query:
        expenses = expenses.filter(
            Q(category__icontains=query) |
            Q(description__icontains=query) |
            Q(amount__icontains=query)
        )
    paginator = Paginator(expenses, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/expense_list.html', {'page_obj': page_obj})

@login_required
def add_expense(request):
    form = Expenseform(request.POST or None)
    if form.is_valid():
        expense_entry = form.save(commit=False)
        expense_entry.user = request.user
        expense_entry.save()
        messages.success(request, "Expense added successfully.")
        return redirect('expense_list')
    return render(request, 'core/add_expense.html', {'form': form})

@login_required
def edit_expense(request, pk):
    expense_entry = get_object_or_404(Expense, pk=pk, user=request.user)
    form = Expenseform(request.POST or None, instance=expense_entry)
    if form.is_valid():
        form.save()
        messages.success(request, "Expense updated successfully.")
        return redirect('expense_list')
    return render(request, 'core/edit_expense.html', {'form': form})

@login_required
def delete_expense(request, pk):
    expense_entry = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense_entry.delete()
        messages.success(request, "Expense deleted successfully.")
        return redirect('expense_list')
    return render(request, 'core/delete_confirm.html', {'object': expense_entry, 'type': 'Expense'})
