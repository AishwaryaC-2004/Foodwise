from django.db import models
from datetime import date

class Restaurant(models.Model):

    restaurant_id = models.CharField(
        max_length=20,
        unique=True
    )

    restaurant_name = models.CharField(
        max_length=100
    )

    city = models.CharField(
        max_length=100
    )

    latitude = models.FloatField()

    longitude = models.FloatField()

    def __str__(self):
        return self.restaurant_name


class MenuItem(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE
    )

    item_name = models.CharField(
        max_length=100
    )

    base_price = models.FloatField()
    checkout_price = models.FloatField(default=0)


    def __str__(self):
        return self.item_name

class ProductionLog(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE
    )

    menu_item = models.ForeignKey(
    MenuItem,
    on_delete=models.CASCADE
    )

    prediction_date = models.DateField(
        default=date.today
    )

    predicted_quantity = models.IntegerField()

    produced_quantity = models.IntegerField()

    sold_quantity = models.IntegerField()

    leftover_quantity = models.IntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.restaurant.restaurant_name} - "
            f"{self.menu_item.item_name}"
        )