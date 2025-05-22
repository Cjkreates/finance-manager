from django.db.models.functions import TruncMonth

from django.db.models import Count
from django.db.models import Q, Sum
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import income, expense
from .forms import incomeform, expenseform, RegisterForm

def home(request):
    return render(request, 'core/home.html')


@login_required
def income_list(request):
    query = request.GET.get('q', '')
    incomes = income.objects.filter(user=request.user)
    if query:
        incomes = incomes.filter(
            Q(source__icontains=query) |
            Q(description__icontains=query) |
            Q(amount__icontains=query)
        )
    return render(request, 'core/income_list.html', {'incomes': incomes})


@login_required
def expense_list(request):
    query = request.GET.get('q', '')
    expenses = expense.objects.filter(user=request.user)
    if query:
        expenses = expenses.filter(
            Q(category__icontains=query) |
            Q(description__icontains=query) |
            Q(amount__icontains=query)
        )
    return render(request, 'core/expense_list.html', {'expenses': expenses})


@login_required
def add_income(request):
    if request.method == 'POST':
        form = incomeform(request.POST)
        if form.is_valid():
            income_entry = form.save(commit=False)
            income_entry.user = request.user
            income_entry.save()
            return redirect('income_list')
    else:
        form = incomeform()
    return render(request, 'core/add_income.html', {'form': form})


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = expenseform(request.POST)
        if form.is_valid():
            expense_entry = form.save(commit=False)
            expense_entry.user = request.user
            expense_entry.save()
            return redirect('expense_list')
    else:
        form = expenseform()
    return render(request, 'core/add_expense.html', {'form': form})





@login_required
def dashboard(request):
    user = request.user

    total_income = income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Expense breakdown by category for pie chart
    expense_data = expense.objects.filter(user=user).values('category').annotate(total=Sum('amount'))

    # Monthly income and expense sums for bar chart
    monthly_income = (
        income.objects.filter(user=user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    monthly_expense = (
        expense.objects.filter(user=user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    # Format data for Chart.js (convert dates to strings)
    expense_categories = [item['category'] for item in expense_data]
    expense_totals = [float(item['total']) for item in expense_data]

    months = sorted(set([item['month'].strftime('%b %Y') for item in monthly_income] + 
                        [item['month'].strftime('%b %Y') for item in monthly_expense]))

    income_totals = []
    expense_totals_monthly = []
    for month in months:
        inc = next((item['total'] for item in monthly_income if item['month'].strftime('%b %Y') == month), 0)
        exp = next((item['total'] for item in monthly_expense if item['month'].strftime('%b %Y') == month), 0)
        income_totals.append(float(inc))
        expense_totals_monthly.append(float(exp))

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

    

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})
