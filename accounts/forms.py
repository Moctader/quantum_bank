from django import forms
from .constants import ACCOUNT_TYPE, GENDER_TYPE
from .models import UserBankAccount, User_Address
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    
    birth_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender=forms.ChoiceField(choices=GENDER_TYPE)
    account_type=forms.ChoiceField(choices=ACCOUNT_TYPE)


    street_address=forms.CharField(max_length=100)
    city=forms.CharField(max_length=100)
    postal_code=forms.IntegerField()
    country=forms.CharField(max_length=100)
    
    class Meta:
        model=User
        fields=['username', 'password1', 'password2', 'first_name', 
                'last_name', 'email', 'birth_date', 'gender', 'account_type', 'street_address', 'city', 
                'postal_code', 'country']
        
    def save(self, commit=True):
        our_user=super().save(commit=False)
        if commit==True:
            our_user.save()
            account_type=self.cleaned_data.get('account_type')
            gender=self.cleaned_data.get('gender')
            country=self.cleaned_data.get('country')
            birth_date=self.cleaned_data.get('birth_date')
            city=self.cleaned_data.get('city')
            street_address=self.cleaned_data.get('street_address')
            postal_code=self.cleaned_data.get('postal_code')
            
            User_Address.objects.create(
                user=our_user,
                city=city,
                street_address=street_address,
                postal_code=postal_code,
                country=country     
            )
            
            UserBankAccount.objects.create(
                user=our_user,
                birth_date=birth_date,
                gender=gender,
                account_type=account_type, 
                account_no=100000+our_user.id
                
            )
        return our_user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                
                'class' : (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                ) 
            })
            
            
            
class UserUpdateForm(forms.ModelForm):
    
    birth_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender=forms.ChoiceField(choices=GENDER_TYPE)
    account_type=forms.ChoiceField(choices=ACCOUNT_TYPE)


    street_address=forms.CharField(max_length=100)
    city=forms.CharField(max_length=100)
    postal_code=forms.IntegerField()
    country=forms.CharField(max_length=100)
    
    class Meta:
        model=User
        fields=['first_name', 'last_name', 'email',]
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                
                'class' : (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                ) 
            })
        
        if self.instance:
            try:
                user_account=self.instance.account
                user_Address=self.instance.address
            except UserBankAccount.DoesNotExist:
                user_account=None
                user_Address=None
                
            if user_account:
                self.fields['birth_date'].initial=user_account.birth_date
                self.fields['gender'].initial=user_account.gender
                self.fields['account_type'].initial=user_account.account_type
                self.fields['street_address'].initial=user_Address.street_address
                self.fields['city'].initial=user_Address.city
                self.fields['postal_code'].initial=user_Address.postal_code
                self.fields['country'].initial=user_Address.country
                
        def save(self, commit=True):
            user=super().save(commit=False)
            
            if commit==True:
                user.save()
                
                user_account, created=UserBankAccount.objects.get_or_create(user=user)
                user_Address, created=User_Address.objects.get_or_create(user=user)
                
                user_account.account_type=self.cleaned_data.get('account_type')
                user_account.gender=self.cleaned_data.get('gender')
                user_account.birth_date=self.cleaned_data.get('birth_date')
                user_account.save()
                
                user_Address.country=self.cleaned_data.get('country')
                user_Address.city=self.cleaned_data.get('city')
                user_Address.street_address=self.cleaned_data.get('street_address')
                user_Address.postal_code=self.cleaned_data.get('postal_code')
                user_Address.save()
                
            return user
                



            
            