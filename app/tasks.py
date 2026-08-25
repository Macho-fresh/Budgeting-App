from celery import shared_task
from .models import *
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

@shared_task
def weekly_task():
    with transaction.atomic():
        weekly_deduct = Transactions.objects.filter(frequency=7)
        amount = weekly_deduct.amount
        budget = Budget.amount
        remaining_money = Budget.remaining_money
        remaining_money = budget - amount
        remaining_money.save()
        print('money deducted!')


@shared_task
def monthly_task():
    with transaction.atomic():
        monthly_deduct = Transactions.objects.filter(frequency=30)
        amount = monthly_deduct.amount
        budget = Budget.amount
        remaining_money = Budget.remaining_money
        remaining_money = budget - amount
        remaining_money.save()
        print('money deducted!')


@shared_task
def yearly_task():
    with transaction.atomic():
        annually_deduct = Transactions.objects.filter(frequency=365)
        amount = annually_deduct.amount
        budget = Budget.amount
        remaining_money = Budget.remaining_money
        remaining_money = budget - amount
        remaining_money.save()
        print('money deducted!')

# @shared_task
# def delete_budget():
#     now = timezone.localdate()
#     budgets = Budget.objects.all()
#     for budget in budgets:
#         budget_timespan = budget.month_year
#         days_difference = (now - budget_timespan).days

#         if now.year == budget_timespan.year and days_difference >= 30:
#             budget.delete()

#     print('checked')

# i removed this because i want the old budgets and its 
# transactions to remian so users can see history of expense then i enforced a 
# rule that only on buget per month


@shared_task
def next_occurence():
    transactions = Transactions.objects.all()
    now = timezone.localdate()
    for transaction in transactions:
        frequency = 0
        if transaction.frequency == 'weekly':
            if now >= transaction.next_occurence:
                transaction.next_occurence = now + timedelta(weeks=1)
        elif transaction.frequency == 'monthly':
            if now >= transaction.next_occurence:
                transaction.next_occurence = now + relativedelta(months=1) 
        elif transaction.frequency == 'yearly':
            if now >= transaction.next_occurence:
                transaction.next_occurence = now + relativedelta(years=1) 

    print('checking...')