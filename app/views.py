from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User

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

        budget = transaction.budget.amount
        remaining_money =  budget - amount
        budget.remaining_money = remaining_money
        budget.save()

        # if theres a frequency, use celery to deduct automatically every (week, month or year)
        # i'll use redis beat
        # if frequency:
        