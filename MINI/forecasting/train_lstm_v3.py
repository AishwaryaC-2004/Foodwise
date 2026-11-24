import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import (
    LabelEncoder,
    MinMaxScaler
)

from sklearn.model_selection import train_test_split

from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input,
    LSTM,
    Dense,
    Dropout,
    Concatenate
)

from tensorflow.keras.callbacks import EarlyStopping

print("Loading dataset...")

df = pd.read_csv(
    "Datasets/foodwise_lstm_dataset_v3.csv"
)

print("Rows:", len(df))

# -----------------------------------
# Encode Restaurant
# -----------------------------------

restaurant_encoder = LabelEncoder()

df["restaurant_encoded"] = (
    restaurant_encoder.fit_transform(
        df["restaurant_id"]
    )
)

# -----------------------------------
# Encode Meal
# -----------------------------------

meal_encoder = LabelEncoder()

df["meal_encoded"] = (
    meal_encoder.fit_transform(
        df["meal_name"]
    )
)

# -----------------------------------
# Sort Properly
# -----------------------------------

df = df.sort_values(
    ["restaurant_id", "meal_name", "week"]
)

# -----------------------------------
# Target Scaling
# -----------------------------------

target_scaler = MinMaxScaler()

df["scaled_orders"] = (
    target_scaler.fit_transform(
        df[["num_orders"]]
    )
)

print("Encoding Complete")
# -----------------------------------
# Context Features
# -----------------------------------

context_features = [
    "restaurant_encoded",
    "meal_encoded",
    "base_price",
    "checkout_price",
    "temperature",
    "rainfall",
    "holiday",
    "emailer_for_promotion",
    "homepage_featured"
]

feature_scaler = MinMaxScaler()

df[context_features] = feature_scaler.fit_transform(
    df[context_features]
)

# -----------------------------------
# Create Sequences
# -----------------------------------

SEQUENCE_LENGTH = 5

X_sequence = []
X_context = []
y = []

print("Creating sequences...")

groups = df.groupby(
    ["restaurant_id", "meal_name"]
)

for _, group in groups:

    group = group.sort_values("week")

    orders = group["scaled_orders"].values

    context = group[
        context_features
    ].values

    if len(group) <= SEQUENCE_LENGTH:
        continue

    for i in range(
        len(group) - SEQUENCE_LENGTH
    ):

        X_sequence.append(
            orders[
                i:i+SEQUENCE_LENGTH
            ]
        )

        X_context.append(
            context[
                i+SEQUENCE_LENGTH
            ]
        )

        y.append(
            orders[
                i+SEQUENCE_LENGTH
            ]
        )

print("Sequences Created")
X_sequence = np.array(
    X_sequence
)

X_context = np.array(
    X_context
)

y = np.array(
    y
)

X_sequence = X_sequence.reshape(
    X_sequence.shape[0],
    SEQUENCE_LENGTH,
    1
)

print("Sequence Shape:", X_sequence.shape)
print("Context Shape:", X_context.shape)
print("Target Shape:", y.shape)
(
    X_seq_train,
    X_seq_test,
    X_ctx_train,
    X_ctx_test,
    y_train,
    y_test
) = train_test_split(
    X_sequence,
    X_context,
    y,
    test_size=0.2,
    random_state=42
)
print("Building V3 Model...")

sequence_input = Input(
    shape=(SEQUENCE_LENGTH, 1)
)

x1 = LSTM(
    64,
    return_sequences=False
)(sequence_input)

x1 = Dropout(
    0.2
)(x1)

context_input = Input(
    shape=(9,)
)

x2 = Dense(
    32,
    activation="relu"
)(context_input)

merged = Concatenate()(
    [x1, x2]
)

x = Dense(
    64,
    activation="relu"
)(merged)

x = Dense(
    32,
    activation="relu"
)(x)

output = Dense(
    1
)(x)

model = Model(
    inputs=[
        sequence_input,
        context_input
    ],
    outputs=output
)

model.compile(
    optimizer="adam",
    loss="mse",
    metrics=["mae"]
)

model.summary()
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

print("Training Started...")

history = model.fit(
    [
        X_seq_train,
        X_ctx_train
    ],
    y_train,
    validation_data=(
        [
            X_seq_test,
            X_ctx_test
        ],
        y_test
    ),
    epochs=20,
    batch_size=32,
    callbacks=[
        early_stop
    ]
)
loss, mae = model.evaluate(
    [
        X_seq_test,
        X_ctx_test
    ],
    y_test
)

print("\nFinal MAE:", mae)
model.save(
    "forecasting/demand_model_v3.keras"
)

joblib.dump(
    feature_scaler,
    "forecasting/feature_scaler.pkl"
)

joblib.dump(
    target_scaler,
    "forecasting/target_scaler.pkl"
)

joblib.dump(
    meal_encoder,
    "forecasting/meal_encoder_v3.pkl"
)

joblib.dump(
    restaurant_encoder,
    "forecasting/restaurant_encoder.pkl"
)

print("\nV3 Model Saved Successfully")