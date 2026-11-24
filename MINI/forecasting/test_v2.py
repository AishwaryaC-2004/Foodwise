import pandas as pd

df = pd.read_csv(
    "Datasets/foodwise_lstm_dataset_v3.csv"
)

print(df["num_orders"].describe())

print("\nMeal Wise Average Demand\n")

print(
    df.groupby("meal_name")["num_orders"]
      .mean()
      .sort_values()
)