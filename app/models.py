from django.db import models
from accounts.models import User
# create db for budget and tranactions

class Category(models.Model):
    category = models.CharField(max_length=100, unique=True)

class Budget(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.IntegerField()
    month_year = models.DateField(unique=True)

class Transctions(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    TYPE_CHOICES = [
        ('INCOME', 'INCOME'),
        ('EXPENSES', 'EXPENSES')
    ]
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)
    amount = models.IntegerField()
    category = models.ForeignKey(Category)
    description = models.CharField(max_length=250)
    transaction_date = models.DateField()
    budget = models.ForeignKey(Budget)
    FREQUENCY_CHOICES = [
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly')
    ]
    frequency = models.CharField(choices=FREQUENCY_CHOICES, max_length=50, null=True)
    next_occurence = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)