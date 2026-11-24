import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# -------------------------
# Load Dataset
# -------------------------

df = pd.read_csv(
    "Datasets/foodwise_lstm_dataset_realistic_prices.csv"
)

print(df.head())

# -------------------------
# Encode Meal Names
# -------------------------

meal_encoder = LabelEncoder()

df["meal_encoded"] = meal_encoder.fit_transform(
    df["meal_name"]
)

# -------------------------
# Features
# -------------------------

features = [
    "week",
    "meal_encoded",
    "base_price",
    "checkout_price",
    "emailer_for_promotion",
    "homepage_featured",
    "temperature",
    "rainfall",
    "holiday"
]

X = df[features]

y = df["num_orders"]

# -------------------------
# Scale Data
# -------------------------

scaler = MinMaxScaler()

X_scaled = scaler.fit_transform(X)

# -------------------------
# Reshape for LSTM
# -------------------------

X_scaled = X_scaled.reshape(
    X_scaled.shape[0],
    1,
    X_scaled.shape[1]
)

# -------------------------
# Split
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42
)

# -------------------------
# Model
# -------------------------

model = Sequential()

model.add(
    LSTM(
        64,
        input_shape=(1, 9)
    )
)

model.add(
    Dropout(0.2)
)

model.add(
    Dense(
        32,
        activation="relu"
    )
)

model.add(
    Dense(1)
)

model.compile(
    optimizer="adam",
    loss="mse",
    metrics=["mae"]
)

# -------------------------
# Train
# -------------------------

history = model.fit(
    X_train,
    y_train,
    epochs=20,
    batch_size=32,
    validation_split=0.2
)

# -------------------------
# Evaluate
# -------------------------

loss, mae = model.evaluate(
    X_test,
    y_test
)

print("MAE =", mae)

# -------------------------
# Save
# -------------------------

model.save(
    "forecasting/demand_model.keras"
)

joblib.dump(
    scaler,
    "forecasting/scaler.pkl"
)

joblib.dump(
    meal_encoder,
    "forecasting/meal_encoder.pkl"
)

print("Model Saved Successfully")