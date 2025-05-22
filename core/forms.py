from django import forms
from .models import income,expense
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class incomeform(forms.ModelForm):
	class Meta:
		model = income
		fields = ['source','amount','date','description']


class expenseform(forms.ModelForm):
	class Meta:
		model = expense
		fields = ['category','amount','date','description']

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']