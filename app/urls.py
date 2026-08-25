from django.urls import path
from .views import *

urlpatterns = [
    path('create-category/', CreateCategory.as_view()),
    path('create-budget/', CreateBudget.as_view()),
    path('create-transactions/', CreateTransactions.as_view()) 
]