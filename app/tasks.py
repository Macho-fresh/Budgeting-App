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

@shared_task
def delete_budget():
    now = timezone.now()
    budget = Budget.objects.all()
    budget_timespan = budget.month_year
    days_difference = (now - budget_timespan).days

    if now == budget_timespan and days_difference == 30:
        Budget.delete()

    print('checked')
