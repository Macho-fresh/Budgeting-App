from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from rest_framework.response import Response
from rest_framework import status

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
