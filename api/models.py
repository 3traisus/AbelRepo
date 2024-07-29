import uuid

from django.db import models


# Create your models here.
class Product(models.Model):
    item_id = models.CharField(max_length=100, primary_key=True, editable=False)
    title = models.CharField(max_length=250, null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency_id = models.CharField(max_length=10, null=False, blank=False)
    available_quantity = models.CharField(max_length=50, null=False, blank=False)
    sold_quantity = models.IntegerField(default=False)
    condition = models.CharField(max_length=50, null=False, blank=False)
    #description = models.TextField(null=True, blank=True)
    attributes = models.JSONField()

    def __str__(self):
        return self.title


class Question(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
    question_id = models.CharField(max_length=100, null=False, blank=False)
    text = models.TextField(null=False, blank=False)
    status = models.CharField(max_length=50, null=False, blank=False)
    answer = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField()

    def __str__(self):
        return self.text