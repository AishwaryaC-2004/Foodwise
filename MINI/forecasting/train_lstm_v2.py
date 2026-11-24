import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# ====================================
# LOAD DATASET
# ====================================

print("Loading dataset...")

df = pd.read_csv(
    "Datasets/foodwise_lstm_dataset_realistic_prices.csv"
)

print("Rows:", len(df))

# ====================================
# SORT DATA
# ====================================

df = df.sort_values(
    ["meal_name", "week"]
)

# ====================================
# SCALE TARGET VARIABLE
# ====================================

scaler = MinMaxScaler()

df["scaled_orders"] = scaler.fit_transform(
    df[["num_orders"]]
)

# ====================================
# CREATE SEQUENCES
# ====================================

SEQUENCE_LENGTH = 5

X = []
y = []

print("Creating sequences...")

for meal in df["meal_name"].unique():

    meal_data = df[
        df["meal_name"] == meal
    ]

    orders = meal_data[
        "scaled_orders"
    ].values

    if len(orders) <= SEQUENCE_LENGTH:
        continue

    for i in range(
        len(orders) - SEQUENCE_LENGTH
    ):

        X.append(
            orders[
                i:i + SEQUENCE_LENGTH
            ]
        )

        y.append(
            orders[
                i + SEQUENCE_LENGTH
            ]
        )

X = np.array(X)
y = np.array(y)

print("Sequences Created:", len(X))

# ====================================
# RESHAPE FOR LSTM
# ====================================

X = X.reshape(
    X.shape[0],
    SEQUENCE_LENGTH,
    1
)

print("X Shape:", X.shape)
print("y Shape:", y.shape)

# ====================================
# TRAIN TEST SPLIT
# ====================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ====================================
# BUILD MODEL
# ====================================

print("Building model...")

model = Sequential()

model.add(
    LSTM(
        64,
        return_sequences=True,
        input_shape=(SEQUENCE_LENGTH, 1)
    )
)

model.add(
    Dropout(0.2)
)

model.add(
    LSTM(32)
)

model.add(
    Dropout(0.2)
)

model.add(
    Dense(
        16,
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

model.summary()

# ====================================
# EARLY STOPPING
# ====================================

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

# ====================================
# TRAIN MODEL
# ====================================

print("Training started...")

history = model.fit(
    X_train,
    y_train,
    validation_data=(
        X_test,
        y_test
    ),
    epochs=20,
    batch_size=32,
    callbacks=[early_stop]
)

# ====================================
# EVALUATE
# ====================================

print("\nEvaluating...")

loss, mae = model.evaluate(
    X_test,
    y_test
)

print("\nFinal MAE:", mae)

# ====================================
# SAVE MODEL
# ====================================

model.save(
    "forecasting/demand_model_v2.keras"
)

joblib.dump(
    scaler,
    "forecasting/scaler_v2.pkl"
)

print("\nModel Saved Successfully")
print("Files Generated:")
print("- demand_model_v2.keras")
print("- scaler_v2.pkl")