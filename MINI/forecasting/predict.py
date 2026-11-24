import pandas as pd
import joblib

from tensorflow.keras.models import load_model

# -----------------------------
# Load Model
# -----------------------------

model = load_model(
    "forecasting/demand_model_v3.keras"
)

# -----------------------------
# Load Scalers
# -----------------------------

feature_scaler = joblib.load(
    "forecasting/feature_scaler.pkl"
)

target_scaler = joblib.load(
    "forecasting/target_scaler.pkl"
)

# -----------------------------
# Load Encoders
# -----------------------------

meal_encoder = joblib.load(
    "forecasting/meal_encoder_v3.pkl"
)

restaurant_encoder = joblib.load(
    "forecasting/restaurant_encoder.pkl"
)

# -----------------------------
# Load Dataset
# -----------------------------

df = pd.read_csv(
    "Datasets/foodwise_lstm_dataset_v3.csv"
)

# -----------------------------
# Prediction Function
# -----------------------------

def predict_demand(
    restaurant_id,
    meal_name,
    temperature=None,
    rainfall=None,
    holiday=None,
    promotion=None
):

    meal_df = df[
        (df["restaurant_id"] == restaurant_id)
        &
        (df["meal_name"] == meal_name)
    ].sort_values(
        "week"
    )

    if len(meal_df) < 6:
        return 0

    # -----------------------------
    # Last 5 Weeks Demand
    # -----------------------------

    last_5 = meal_df["num_orders"].values[-5:]

    seq_scaled = target_scaler.transform(
        last_5.reshape(-1, 1)
    )

    X_seq = seq_scaled.reshape(
        1,
        5,
        1
    )

    # -----------------------------
    # Latest Context Row
    # -----------------------------

    latest = meal_df.iloc[-1]

    # -----------------------------
    # Simulator Overrides
    # -----------------------------

    if temperature is None:
        temperature = latest["temperature"]

    if rainfall is None:
        rainfall = latest["rainfall"]

    if holiday is None:
        holiday = latest["holiday"]

    if promotion is None:
        promotion = latest["emailer_for_promotion"]

    # -----------------------------
    # Context Features
    # -----------------------------

    context = [[

        restaurant_encoder.transform(
            [restaurant_id]
        )[0],

        meal_encoder.transform(
            [meal_name]
        )[0],

        latest["base_price"],

        latest["checkout_price"],

        temperature,

        rainfall,

        holiday,

        promotion,

        latest["homepage_featured"]

    ]]

    context = feature_scaler.transform(
        context
    )

    # -----------------------------
    # Predict
    # -----------------------------

    prediction = model.predict(
        [X_seq, context],
        verbose=0
    )

    demand = target_scaler.inverse_transform(
        prediction.reshape(-1, 1)
    )

    return max(
        0,
        int(demand[0][0])
    )