from django import forms
from .models import Transection

class TransectionForm(forms.ModelForm):
    class Meta:
        model=Transection
        fields=['amount', 'transection_type']
        
    def __init__(self, *args, **kwargs):
        self.account=kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transection_type'].disabled=True
        self.fields['transection_type'].widget=forms.HiddenInput()
        
    def save(self, commit=True):
        self.instance.account=self.account
        self.instance.balance_after_transection=self.account.balance 
        return super().save() 


class DepositForm(TransectionForm):
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount
    
class WithdrawForm(TransectionForm):
    def clean_amount(self):
        account=self.account
        balance=account.balance
        amount=self.cleaned_data.get('amount')
        min_withdraw=500
        max_withdraw=2000
        if amount<min_withdraw:
            raise forms.ValidationError(
                f'you can withdraw at least : {min_withdraw}$'
            )
            
        if amount>max_withdraw:
            raise forms.ValidationError(
                f'you can withdraw at most : {max_withdraw}§'
            )
            
        if amount>balance:
            raise forms.ValidationError(
                f'you have {balance}$ in your account. you can not withdraw more than your account balance'
                
            )
        return amount

class LoanRequestForm(TransectionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        return amount
        