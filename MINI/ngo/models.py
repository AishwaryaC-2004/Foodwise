from django.db import models
from restaurant.models import ProductionLog

class NGO(models.Model):

    ngo_id = models.CharField(
        max_length=20,
        unique=True
    )

    ngo_name = models.CharField(
        max_length=100
    )

    city = models.CharField(
        max_length=100
    )

    latitude = models.FloatField()

    longitude = models.FloatField()

    capacity = models.IntegerField()

    def __str__(self):
        return self.ngo_name


class NGORequirement(models.Model):

    ngo = models.ForeignKey(
        NGO,
        on_delete=models.CASCADE
    )

    food_item = models.CharField(
        max_length=100
    )

    quantity_required = models.IntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.food_item
class DonationMatch(models.Model):

    ngo = models.ForeignKey(
        NGO,
        on_delete=models.CASCADE
    )

    production_log = models.ForeignKey(
        ProductionLog,
        on_delete=models.CASCADE
    )

    allocated_quantity = models.IntegerField()

    status = models.CharField(
        max_length=20,
        default="Pending"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.ngo.ngo_name}"