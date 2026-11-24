from django.core.management.base import BaseCommand
from restaurant.models import Restaurant, MenuItem
import pandas as pd


class Command(BaseCommand):

    help = "Import FoodWise Dataset"

    def handle(self, *args, **kwargs):

        file_path = "Datasets/foodwise_lstm_dataset_realistic_prices.csv"

        self.stdout.write("Loading dataset...")

        df = pd.read_csv(file_path)

        # Clear existing data

        MenuItem.objects.all().delete()
        Restaurant.objects.all().delete()

        # ==========================
        # Import Restaurants
        # ==========================

        restaurants_df = df[
            [
                "restaurant_id",
                "restaurant_name",
                "city"
            ]
        ].drop_duplicates()

        restaurant_map = {}

        for _, row in restaurants_df.iterrows():

            restaurant = Restaurant.objects.create(
                restaurant_id=row["restaurant_id"],
                restaurant_name=row["restaurant_name"],
                city=row["city"],
                latitude=0,
                longitude=0
            )

            restaurant_map[row["restaurant_id"]] = restaurant

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(restaurant_map)} restaurants imported."
            )
        )

        # ==========================
        # Import Unique Menu Items
        # ==========================

        unique_menu = df[
            [
                "restaurant_id",
                "meal_name"
            ]
        ].drop_duplicates()

        menu_count = 0

        for _, row in unique_menu.iterrows():

            restaurant_id = row["restaurant_id"]

            meal_name = row["meal_name"]

            meal_rows = df[
                (df["restaurant_id"] == restaurant_id)
                &
                (df["meal_name"] == meal_name)
            ]

            first_row = meal_rows.iloc[0]

            MenuItem.objects.create(
                restaurant=restaurant_map[
                    restaurant_id
                ],
                item_name=meal_name,
                base_price=first_row["base_price"],
                checkout_price=first_row["checkout_price"]
            )

            menu_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{menu_count} unique menu items imported."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Import completed successfully."
            )
        )