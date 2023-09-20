from django.contrib import admin
from .models import UserBankAccount, User_Address

# Register your models here.
admin.site.register(UserBankAccount)
admin.site.register(User_Address)