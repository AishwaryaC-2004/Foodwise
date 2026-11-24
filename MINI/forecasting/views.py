from django.shortcuts import render

from restaurant.models import (
    Restaurant,
    MenuItem
)

from .predict import predict_demand
def forecast_page(request):

    restaurant_id = request.session.get(
        "restaurant_id"
    )

    restaurant = Restaurant.objects.get(
        restaurant_id=restaurant_id
    )

    menu_items = MenuItem.objects.filter(
        restaurant=restaurant
    )

    forecasts = []

    for item in menu_items:

        prediction = predict_demand(
            week=146,
            meal_name=item.item_name,
            base_price=item.base_price,
            checkout_price=item.checkout_price,
            temperature=30,
            rainfall=50,
            holiday=0
        )

        forecasts.append(
            {
                "item": item.item_name,
                "predicted": prediction,
                "recommended": int(prediction * 1.10)
            }
        )

    return render(
        request,
        "forecasting/forecast.html",
        {
            "forecasts": forecasts
        }
    )