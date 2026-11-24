from django.shortcuts import render, redirect
from .models import Restaurant
from .models import ProductionLog
from datetime import date
from .models import ProductionLog, MenuItem
from ngo.models import DonationMatch
from forecasting.predict import predict_demand
from forecasting.predict import predict_demand
from ngo.models import NGO
from geopy.distance import geodesic
from django.db.models import Sum

def login_view(request):

    if request.method == 'POST':

        restaurant_id = request.POST.get('restaurant_id')

        try:
            restaurant = Restaurant.objects.get(
                restaurant_id=restaurant_id
            )

            request.session["restaurant_id"] = restaurant.id

            return redirect(
                "dashboard"
            )

        except Restaurant.DoesNotExist:

            return render(
                request,
                'restaurant/login.html',
                {
                    'error': 'Invalid Restaurant ID'
                }
            )

    return render(
        request,
        'restaurant/login.html'
    )


def dashboard(request):
    
    restaurant_id = request.session.get(
        "restaurant_id"
    )

    if not restaurant_id:
        return redirect("login")

    restaurant = Restaurant.objects.get(
        id=restaurant_id
    )

    menu_items = restaurant.menuitem_set.all()
    from ngo.models import DonationMatch

    donations = DonationMatch.objects.filter(
        production_log__restaurant=restaurant,
        status="Accepted"
    )
    return render(
        request,
        "restaurant/dashboard.html",
        {
            "restaurant": restaurant,
            "menu_items": menu_items,
            "donations": donations
        }
    )
def prediction(request):

    restaurant_id = request.session.get(
        "restaurant_id"
    )

    restaurant = Restaurant.objects.get(
        id=restaurant_id
    )

    menu_items = MenuItem.objects.filter(
        restaurant=restaurant
    )[:20]

    predictions = []

    for item in menu_items:

        demand = predict_demand(
            restaurant.restaurant_id,
            item.item_name
        )
        recommended = int(demand * 1.10)
        predictions.append({
            "item": item.item_name,
            "demand": demand,
            "recommended": recommended
        })

    return render(
        request,
        "restaurant/prediction.html",
        {
            "restaurant": restaurant,
            "predictions": predictions
        }
    )
def production(request):

    restaurant_id = request.session.get(
        "restaurant_id"
    )

    restaurant = Restaurant.objects.get(
        id=restaurant_id
    )

    menu_items = MenuItem.objects.filter(
        restaurant=restaurant
    )

    if request.method == "POST":

        for item in menu_items:

            predicted = int(
                request.POST.get(
                    f"predicted_{item.id}",
                    0
                )
            )

            produced = int(
                request.POST.get(
                    f"produced_{item.id}",
                    0
                )
            )

            sold = int(
                request.POST.get(
                    f"sold_{item.id}",
                    0
                )
            )

            leftover = produced - sold

            ProductionLog.objects.create(
                restaurant=restaurant,
                menu_item=item,
                prediction_date=date.today(),
                predicted_quantity=predicted,
                produced_quantity=produced,
                sold_quantity=sold,
                leftover_quantity=leftover
            )

        request.session["restaurant_id"] = restaurant.id

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "restaurant/production.html",
        {
            "restaurant": restaurant,
            "menu_items": menu_items
        }
    )
def landing(request):
    return render(
        request,
        "landing.html"
    )
def logout_view(request):

    request.session.flush()

    return redirect("/")
def donations(request):

    restaurant_id = request.session.get(
        "restaurant_id"
    )

    restaurant = Restaurant.objects.get(
        id=restaurant_id
    )

    donations = DonationMatch.objects.filter(
        production_log__restaurant=restaurant,
        status="Accepted"
    )

    return render(
        request,
        "restaurant/donations.html",
        {
            "restaurant": restaurant,
            "donations": donations
        }
    )
def simulator(request):

    restaurant_id = request.session.get(
        "restaurant_id"
    )

    restaurant = Restaurant.objects.get(
        id=restaurant_id
    )

    results = []

    if request.method == "POST":

        temperature = float(
            request.POST["temperature"]
        )

        rainfall = float(
            request.POST["rainfall"]
        )

        holiday = int(
            request.POST["holiday"]
        )

        promotion = int(
            request.POST["promotion"]
        )

        menu_items = MenuItem.objects.filter(
            restaurant=restaurant
        )[:15]

        for item in menu_items:

            demand = predict_demand(
                restaurant.restaurant_id,
                item.item_name,
                temperature,
                rainfall,
                holiday,
                promotion
            )

            results.append({
                "item": item.item_name,
                "demand": demand,
                "recommended": int(demand * 1.10)
            })

    return render(
        request,
        "restaurant/simulator.html",
        {
            "restaurant": restaurant,
            "results": results
        }
    )
def map_view(request):

    restaurant_id = request.session.get(
        "restaurant_id"
    )

    restaurant = Restaurant.objects.get(
        id=restaurant_id
    )

    ngos = NGO.objects.all()

    nearest_ngo = None
    min_distance = float("inf")

    for ngo in ngos:

        distance = geodesic(
            (
                restaurant.latitude,
                restaurant.longitude
            ),
            (
                ngo.latitude,
                ngo.longitude
            )
        ).km

        if distance < min_distance:

            min_distance = distance
            nearest_ngo = ngo

    return render(
        request,
        "restaurant/map.html",
        {
            "restaurant": restaurant,
            "nearest_ngo": nearest_ngo,
            "distance": round(
                min_distance,
                2
            ),
            "ngos": ngos
        }
    )
def analytics(request):

    restaurant_id = request.session.get(
        "restaurant_id"
    )

    restaurant = Restaurant.objects.get(
        id=restaurant_id
    )

    logs = ProductionLog.objects.filter(
        restaurant=restaurant
    )

    donations = DonationMatch.objects.filter(
        production_log__restaurant=restaurant,
        status="Accepted"
    )

    total_forecasted = (
        logs.aggregate(
            Sum("predicted_quantity")
        )["predicted_quantity__sum"] or 0
    )

    total_produced = (
        logs.aggregate(
            Sum("produced_quantity")
        )["produced_quantity__sum"] or 0
    )

    total_sold = (
        logs.aggregate(
            Sum("sold_quantity")
        )["sold_quantity__sum"] or 0
    )

    total_leftover = (
        logs.aggregate(
            Sum("leftover_quantity")
        )["leftover_quantity__sum"] or 0
    )

    total_donated = (
        donations.aggregate(
            Sum("allocated_quantity")
        )["allocated_quantity__sum"] or 0
    )

    if total_leftover > 0:

        donation_efficiency = round(
            (total_donated / total_leftover) * 100,
            2
        )

    else:

        donation_efficiency = 0

    return render(
        request,
        "restaurant/analytics.html",
        {
            "restaurant": restaurant,
            "forecasted": total_forecasted,
            "produced": total_produced,
            "sold": total_sold,
            "leftover": total_leftover,
            "donated": total_donated,
            "efficiency": donation_efficiency
        }
    )