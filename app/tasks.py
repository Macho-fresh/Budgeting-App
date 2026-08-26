from celery import shared_task
from .models import *
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

@shared_task
def weekly_task():
    today = timezone.localdate()
    with transaction.atomic():
        weekly_deduct = Transactions.objects.filter(frequency='weekly',next_occurence__lte=today)
        for recurring_deduct in weekly_deduct:
            amount = recurring_deduct.amount
            budget = recurring_deduct.budget
            budget.remaining_money -= amount
            budget.save()
            # create a transaction

            Transactions.objects.create(
            owner = recurring_deduct.owner,
            type = recurring_deduct.type,
            amount = recurring_deduct.amount,
            category = recurring_deduct.category,
            description = recurring_deduct.description,
            transaction_date = timezone.localdate(),
            budget = recurring_deduct.budget,
            frequency = ''
        )
            print('money deducted!')


@shared_task
def monthly_task():
    today = timezone.localdate()
    with transaction.atomic():
        monthly_deduct = Transactions.objects.filter(frequency='monthly',next_occurence__lte=today)
        for recurring_deduct in monthly_deduct:
            amount = recurring_deduct.amount
            budget = recurring_deduct.budget
            budget.remaining_money -= amount
            budget.save()
            # create a transaction

            Transactions.objects.create(
            owner = recurring_deduct.owner,
            type = recurring_deduct.type,
            amount = recurring_deduct.amount,
            category = recurring_deduct.category,
            description = recurring_deduct.description,
            transaction_date = timezone.localdate(),
            budget = recurring_deduct.budget,
            frequency = ''
        )
            print('money deducted!')



@shared_task
def yearly_task():
    today = timezone.localdate()
    with transaction.atomic():
        yearly_deduct = Transactions.objects.filter(frequency='yearly',next_occurence__lte=today)
        for recurring_deduct in yearly_deduct:
            amount = recurring_deduct.amount
            budget = recurring_deduct.budget
            budget.remaining_money -= amount
            budget.save()
            # create a transaction

            Transactions.objects.create(
            owner = recurring_deduct.owner,
            type = recurring_deduct.type,
            amount = recurring_deduct.amount,
            category = recurring_deduct.category,
            description = recurring_deduct.description,
            transaction_date = timezone.localdate(),
            budget = recurring_deduct.budget,
            frequency = ''
        )
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
                transaction.next_occurence += timedelta(weeks=1)
                transaction.save()
        elif transaction.frequency == 'monthly':
            if now >= transaction.next_occurence:
                transaction.next_occurence += relativedelta(months=1)
                transaction.save()
        elif transaction.frequency == 'yearly':
            if now >= transaction.next_occurence:
                transaction.next_occurence += relativedelta(years=1) 
                transaction.save()

    print('checking...')