from restaurant.models import Restaurant

for r in Restaurant.objects.all()[:5]:
    print(
        r.restaurant_name,
        r.city,
        r.latitude,
        r.longitude
    )