from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

class CreateCategory(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        category = request.data.get('category')

        Category.objects.create(
            category_name = category
        )

        return Response({
            'message': 'Category created successfully'
        }, status = status.HTTP_201_CREATED)

class CreateBudget(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        name = request.data.get('name')
        amount = request.data.get('amount')
        month_year = request.data.get('month_year')

        owner = User.objects.get(id=request.user.id)
        
        try:

            Budget.objects.get(owner = owner, month_year=month_year)
            return Response({
                'message': 'A budget for this month already exists'
            }, status = status.HTTP_409_CONFLICT)

        except Budget.DoesNotExist:

            Budget.objects.create(
                owner = owner,
                name = name,
                amount = amount,
                month_year = month_year,
                remaining_money=amount 
            )

            return Response({
                'message': 'Budget created successfully'
            }, status = status.HTTP_201_CREATED)    

# when a user sends in  transaction and its recurring, celery dedducts the money automtically every month]\
class CreateTransactions(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        t = request.data.get('type')
        amount = request.data.get('amount')
        category_id = request.data.get('category')
        description = request.data.get('description')
        transaction_date = request.data.get('transaction_date')
        frequency = request.data.get('frequency')
        now = timezone.localdate()

        budget = Budget.objects.get(month_year=now)
        owner = User.objects.get(id = request.user.id)
        category = Category.objects.get(id=category_id) 
        # with transaction.atomic()
        # i removed the transaction because it conflicts with the transaction below and 
        # im too lazy to change all the names
        transaction = Transactions.objects.create(
            owner = owner,
            type = t,
            amount = amount,
            category = category,
            description = description,
            transaction_date = transaction_date,
            budget = budget,
            frequency = frequency
        )
        print(transaction)


        if transaction.type == 'expenses':
            budget = transaction.budget
            budget.remaining_money -= transaction.amount
            budget.save()

        elif transaction.type == 'income':
            budget = transaction.budget
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
                transaction.next_occurence = now + timedelta(weeks=1)
                transaction.save()
            elif frequency == 'monthly':
                frequency_int = 30
                transaction.next_occurence = now + relativedelta(months=1)
                transaction.save()
            elif frequency == 'yearly':
                frequency_int = 365
                transaction.next_occurence = now + relativedelta(years=1)
                transaction.save()


            def sheduletask():
                interval, _ = IntervalSchedule.objects.get_or_create(
                    every=frequency_int,
                    period=IntervalSchedule.SECONDS
                )

                PeriodicTask.objects.get_or_create(
                    interval = interval,
                    name = "check_recurring_transactions",
                    task= f"app.tasks.{frequency}_task"
                )

            # if the month is in the current year and when its subtracted from the created_at month its == 30 then we delete 
            # if its not in the current year well check every 30 days if timezone.now() year is equall to the year, if it is well run the above condition

            return Response({
                "message": "Transaction added"
            }, status=status.HTTP_201_CREATED)

class DeleteCategory(APIView):
    def delete(self, request, id):
        category = Category.objects.get(id = id)
        category.delete()

        return Response({
            'message': 'Categoryy deleted'
        }, status = status.HTTP_200_OK)
