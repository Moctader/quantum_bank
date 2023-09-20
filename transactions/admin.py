from django.contrib import admin
from .models import Transection
# Register your models here.
@admin.register(Transection)
class TransectionAdmin(admin.ModelAdmin):
    list_display=['account', 'amount', 'balance_after_transection', 'transection_type', 'loan_approve']
    
    def save_model(self, request, obj, form , change):
        obj.account.balance += obj.amount
        obj.balance_after_transection = obj.account.balance
        obj.account.save()
        super().save_model(request, obj, form, change)