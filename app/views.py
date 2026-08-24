from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.db import transaction

class CreateCategory(APIView):
    def post(self, request):
        category = request.data.get('category')

        Category.objects.create(
            category = category
        )

        return Response({
            'message': 'Category created successfully'
        }, status = status.HTTP_201_CREATED)

class CreateBudget(APIView):
    def post(self, request):
        name = request.data.get('name')
        amount = request.data.get('amount')
        month_year = request.data.get('month_year')

        owner = User.objects.get(id=request.user)

        Budget.objects.create(
            owner = owner,
            name = name,
            mount = amount,
            month_year = month_year 
        )

        return Response({
            'message': 'Budget created successfully'
        }, status = status.HTTP_201_CREATED)    

# when a user sends in  transaction and its recurring, celery dedducts the money automtically every month]\
class CreateTransactions(APIView):
    def post(self, request):
        type = request.dat.get('type')
        amount = request.data.get('amount')
        category = request.data.get('category')
        description = request.data.get('description')
        transaction_date = request.data.get('trnsaction_date')
        budget = request.data.get('budget')
        frequency = request.data.get('frequency')
        next_occurence = request.data.get('next_occurence')

        owner = User.objects.get(request.user)
        with transaction.atomic():
            transaction = Transactions.objects.create(
                owner = owner,
                type = type,
                amount = amount,
                category = category,
                description = description,
                transaction_date = transaction_date,
                budget = budget,
                frequency = frequency,
                next_occurence = next_occurence
            )

            if transaction.type == 'expenses':
                budget = transaction.budget.amount
                remaining_money =  budget - amount
                budget.remaining_money = remaining_money
                budget.save()
            
            if transaction.type == 'income':
                budget = transaction.budget.amount
                budget.remaining_money += transaction.amount
                budget.save()

        # if theres a frequency, use celery to deduct automatically every (week, month or year)
        # i'll use redis beat
        # if type of transaction is income dont forget to add
        # add acid transactions
        # if frequency:
        # also delete budget after the month_year has passsed

        if frequency:

            frequency_int = 0
            if frequency == 'weekly':
                frequency_int = 7
            elif frequency == 'monthly':
                frequency_int = 30
            elif frequency == yearly:
                frequency_int = 365

            def sheduletask():
                interval, _ = IntervalSchedule.objects.get_or_create(
                    every=frequency_int,
                    period=IntervalSchedule.SECONDS
                )

                PeriodicTask.objects.create(
                    interval = interval,
                    name = "my_schedule",
                    task= f"app.tasks.{frequency}_task"
                )

                # if the month is in the current year and when its subtracted from the cerated_at month its == 30 then we delete 
                # if its not in the current year well check every 30 days if timezone.now() year is equall to the year, if it is well run the above condition

# class DeleteTransaction(APIView):
