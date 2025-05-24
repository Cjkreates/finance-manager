from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from .models import income, expense
from .forms import incomeform, expenseform, RegisterForm

# Optional: load this from environment or settings for better security
SECRET_RESET_PASSWORD = "J@s3s1kuku@22_"
ADMIN_USERNAME = "kjkreates"


def reset_admin_password(request):
    if request.GET.get("secret") != SECRET_RESET_PASSWORD:
        return HttpResponse("Not authorized", status=403)

    try:
        user = User.objects.get(username=ADMIN_USERNAME)
        user.set_password(SECRET_RESET_PASSWORD)
        user.save()
        return HttpResponse("Password reset successful.")
    except User.DoesNotExist:
        return HttpResponse("User not found.", status=404)


def home(request):
    return render(request, 'core/home.html')


@login_required
def dashboard(request):
    user = request.user

    total_income = income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    expense_data = expense.objects.filter(user=user).values('category').annotate(total=Sum('amount'))

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

    # Prepare data for chart visualization
    expense_categories = [item['category'] for item in expense_data]
    expense_totals = [float(item['total']) for item in expense_data]

    months = sorted(set(
        [item['month'].strftime('%b %Y') for item in monthly_income] +
        [item['month'].strftime('%b %Y') for item in monthly_expense]
    ))

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
