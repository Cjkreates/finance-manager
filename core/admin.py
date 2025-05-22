from django.contrib import admin

from . models import income,expense

admin.site.register(income)
admin.site.register(expense)