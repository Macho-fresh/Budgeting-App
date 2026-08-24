from django.db import models
from accounts.models import User
# create db for budget and tranactions

class Category(models.Model):
    category = models.CharField(max_length=100, unique=True)

class Budget(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.IntegerField()
    remaining_money = models.IntegerField()
    month_year = models.DateField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Transactions(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    TYPE_CHOICES = [
        ('income', 'income'),
        ('expenses', 'expenses')
    ]
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)
    amount = models.IntegerField()
    category = models.ForeignKey(Category)
    description = models.CharField(max_length=250)
    transaction_date = models.DateField()
    budget = models.ForeignKey(Budget)
    FREQUENCY_CHOICES = [
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
        ('yearly', 'yearly')
    ]
    frequency = models.CharField(choices=FREQUENCY_CHOICES, max_length=50, blank=True)
    next_occurence = models.DateField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)