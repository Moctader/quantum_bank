from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.views.generic import CreateView, ListView
from transactions.forms import DepositForm, WithdrawForm, LoanRequestForm
from transactions.models import Transection
from django.utils import timezone
from django.contrib import messages
from .constants import TRANSECTIONS_TYPE
from transactions.constants import LOAN, DEPOSIT, WITHDRAWAL, LOAN_PAID
from datetime import datetime
from django.views import View




# Create your views here.
class TransectionCreateMixin(LoginRequiredMixin, CreateView):
    template_name='transactions/transaction_form.html' 
    success_url=reverse_lazy('transaction_report')
    model=Transection
    title=''
    
    def get_form_kwargs(self):
        kwargs= super().get_form_kwargs()
        kwargs.update({
            'account':self.request.user.account
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context.update({
            'title':self.title
        })
        return context


class DepositMoneyView(TransectionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transection_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        # if not account.initial_deposit_date:
        #     now = timezone.now()
        #     account.initial_deposit_date = now
        account.balance += amount 
        account.save(
            update_fields=[
                'balance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )

        return super().form_valid(form)



class WithdrwalMoneyView(TransectionCreateMixin):
    form_class=WithdrawForm
    title='Withdraw Money'
    
    def get_initial(self):
        initial={'transection_type':WITHDRAWAL}
        return initial
    
    def form_valid(self, form):
        amount=form.cleaned_data.get('amount')
        self.request.user.account.balance -=form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])
        
        messages.success(
            self.request,
            f'successfully withdrwan {"{:,.2f}".format(float(amount))} from your account'
            
        )
        return super().form_valid(form)

class LoanRequestView(TransectionCreateMixin):
    form_class=LoanRequestForm
    title='Request For Loan'
    

    def get_initial(self):
        initial = {'transection_type': LOAN}
        return initial

    
    def form_valid(self, form):
        amount=form.cleaned_data.get('amount')
        current_loan_count=Transection.objects.filter(
            account=self.request.user.account, transection_type=3, loan_approve=True
        ).count()
        
        if current_loan_count>=3:
            return HttpResponse('you have crossed loan limit')
        
        messages.success(
            self.request,
            f'loan requested for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )
        
        return super().form_valid(form)

class TransectionReportView(LoginRequiredMixin, ListView):
    template_name='transactions/transaction_report.html'
    model=Transection
    form_data={}
    balance=0
    
    def get_queryset(self):
        queryset= super().get_queryset().filter(
            account= self.request.user.account

        )
        start_date_str=self.request.GET.get('start_date')
        end_date_str=self.request.GET.get('end_date')
       
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transection.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']

        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context.update({
            'account':self.request.user.account
        })
        return context

class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan=get_object_or_404(Transection, id=loan_id) 
        print(loan)
        
        if loan.loan_approve:
            user_account=loan.account
            
            if loan.amount<user_account.balance:
                user_account.balance -=loan.amount
                loan.balance_after_transection=user_account.balance
                user_account.save()
                loan.loan_approve=True
                loan.transection_type=LOAN_PAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(
                    self.request, 
                    f'loan amount is greater than available balance'
                )        
        return redirect('transactions:loan_list')

class LoanListView(LoginRequiredMixin, ListView):
    model=Transection
    template_name='transactions/loan_request.html'
    context_object_name='loans'
    
    def get_queryset(self):
        user_account=self.request.user.account
        queryset=Transection.objects.filter(account=user_account, transection_type=3)
        print(queryset)
        return queryset