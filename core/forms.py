from django import forms
from .models import Income,Expense
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class Incomeform(forms.ModelForm):
	class Meta:
		model = Income
		fields = ['source','amount','date','description']


class Expenseform(forms.ModelForm):
	class Meta:
		model = Expense
		fields = ['category','amount','date','description']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
