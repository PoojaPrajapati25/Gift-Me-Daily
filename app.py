from flask import Flask, render_template, request, redirect, url_for, session

import joblib
import pandas as pd
import sqlite3
import requests
import math
from datetime import datetime

app = Flask(__name__)

shipping_model = joblib.load("models/shipping_model.pkl")

delivery_model = joblib.load("models/delivery_model.pkl")

product_encoder = joblib.load("models/product_encoder.pkl")

feature_columns = joblib.load("models/feature_columns.pkl")

pin_coordinates = joblib.load("models/pin_coordinates.pkl")

app.secret_key = "giftmedaily_secret_key"

# Fixed Login Credentials

USERNAME = "admin"
PASSWORD = "admin123"

products = list(product_encoder.classes_)

# Fixed dispatch location
SOURCE_PIN = "324007"
SOURCE_LAT = 25.1901
SOURCE_LON = 76.1223

# Normalize PIN values
pin_coordinates["pincode"] = (
    pin_coordinates["pincode"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(6)
)

def get_destination_coordinates(destination_pin):

    result = pin_coordinates[
        pin_coordinates["pincode"] == destination_pin
    ]

    if result.empty:
        raise ValueError(
            "Coordinates not available for this PIN code."
        )

    latitude = float(result.iloc[0]["latitude"])
    longitude = float(result.iloc[0]["longitude"])

    if not math.isfinite(latitude) or not math.isfinite(longitude):
        raise ValueError("Invalid PIN coordinates.")

    return latitude, longitude


def calculate_road_distance(destination_lat, destination_lon):

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{SOURCE_LON},{SOURCE_LAT};"
        f"{destination_lon},{destination_lat}"
    )

    try:
        response = requests.get(
            url,
            params={"overview": "false"},
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            raise ValueError("Road route not found.")

        distance_km = data["routes"][0]["distance"] / 1000

        if not math.isfinite(distance_km) or distance_km <= 0:
            raise ValueError("Invalid road distance.")

        return distance_km

    except requests.RequestException:
        raise ValueError(
            "Road distance service is temporarily unavailable."
        )

@app.route("/")
def home():

    if "user" in session:
        return redirect(url_for("dashboard"))

    return render_template("home.html")

@app.route("/login")
def login():

    if "user" in session:
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def check_login():

    username = request.form["username"].strip()
    password = request.form["password"].strip()

    if username == USERNAME and password == PASSWORD:

        session["user"] = username

        return redirect(url_for("dashboard"))

    return render_template(
        "login.html",
        error="Invalid Username or Password"
    )

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database/giftmedaily.db")
    cursor = conn.cursor()

    # Total Predictions

    cursor.execute("""
        SELECT COUNT(*)
        FROM prediction_history
    """)

    total_predictions = cursor.fetchone()[0]

    # Average Shipping Cost

    cursor.execute("""
        SELECT ROUND(AVG(shipping_cost),2)
        FROM prediction_history
    """)

    avg_shipping = cursor.fetchone()[0] or 0

    # Average Delivery Days

    cursor.execute("""
        SELECT ROUND(AVG(delivery_days),2)
        FROM prediction_history
    """)

    avg_delivery = cursor.fetchone()[0] or 0

    # Most Predicted Product

    cursor.execute("""
        SELECT product_name
        FROM prediction_history
        GROUP BY product_name
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    top_product = row[0] if row else "No Data"

    
    # ================= SHIPPING BAR CHART =================

    cursor.execute("""
    SELECT product_name,
    ROUND(AVG(shipping_cost),2)
    FROM prediction_history
    GROUP BY product_name
    ORDER BY product_name
    """)

    shipping_chart = cursor.fetchall()

    shipping_labels = [row[0] for row in shipping_chart]
    shipping_values = [row[1] for row in shipping_chart]
    
    # ================= DELIVERY LINE CHART =================

    cursor.execute("""
    SELECT prediction_date,
    delivery_days
    FROM prediction_history
    WHERE delivery_days IS NOT NULL
    ORDER BY id
    """)

    delivery_chart = cursor.fetchall()

    delivery_labels = [row[0] for row in delivery_chart]
    delivery_values = [row[1] for row in delivery_chart]

    # ================= PRODUCT PIE CHART =================

    cursor.execute("""
    SELECT product_name,
    COUNT(*)
    FROM prediction_history
    GROUP BY product_name
    ORDER BY COUNT(*) DESC
    """)

    product_chart = cursor.fetchall()

    product_labels = [row[0] for row in product_chart]
    product_values = [row[1] for row in product_chart]
    
    conn.close()

    return render_template(

    "dashboard.html",

    username=session["user"],

    total_predictions=total_predictions,
    avg_shipping=avg_shipping,
    avg_delivery=avg_delivery,
    top_product=top_product,

    shipping_labels=shipping_labels,
    shipping_values=shipping_values,

    delivery_labels=delivery_labels,
    delivery_values=delivery_values,

    product_labels=product_labels,
    product_values=product_values
)

@app.route("/prediction")
def prediction():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "prediction.html",
        products=products
    )

from datetime import datetime


@app.route("/predict", methods=["POST"])
def predict():

    if "user" not in session:
        return redirect(url_for("login"))

    try:

        # 1. Read user inputs
        product_value = float(request.form["product_value"])
        weight = float(request.form["weight"])
        destination_pin = request.form["destination_pin"].strip()
        product_name = request.form["product_name"].strip()

        # 2. Validate inputs
        if not destination_pin.isdigit() or len(destination_pin) != 6:
            raise ValueError("Enter a valid 6-digit PIN code.")

        if not math.isfinite(product_value) or product_value < 0:
            raise ValueError("Enter a valid product value.")

        if not math.isfinite(weight) or weight <= 0:
            raise ValueError("Weight must be greater than zero.")

        # 3. Get destination coordinates
        destination_lat, destination_lon = (
            get_destination_coordinates(destination_pin)
        )

        # 4. Calculate road distance automatically
        road_distance = calculate_road_distance(
            destination_lat,
            destination_lon
        )

        # 5. Encode product name
        try:
            encoded_product = product_encoder.transform(
                [product_name]
            )[0]
        except ValueError:
            raise ValueError("Product name is not supported by the model.")

        # 6. Prepare model features
        feature_values = {
            "product_value": product_value,
            "weight": weight,
            "product_name": encoded_product,
            "destination_latitude": destination_lat,
            "destination_longitude": destination_lon,
            "road_distance_km": road_distance
        }

        # Use exact saved training feature order
        input_df = pd.DataFrame(
            [[feature_values[col] for col in feature_columns]],
            columns=feature_columns
        )

        # 7. Predict shipping cost
        shipping_cost = round(
            float(shipping_model.predict(input_df)[0]), 2
        )

        # 8. Predict delivery days
        delivery_days = round(
            float(delivery_model.predict(input_df)[0]), 2
        )

        # Avoid negative predictions
        shipping_cost = max(0, shipping_cost)
        delivery_days = max(0, delivery_days)

        # 9. Save prediction in database
        conn = sqlite3.connect("database/giftmedaily.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO prediction_history
            (
                username,
                product_name,
                product_value,
                destination_pin,
                weight,
                shipping_cost,
                delivery_days,
                prediction_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user"],
            product_name,
            product_value,
            destination_pin,
            weight,
            shipping_cost,
            delivery_days,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))

        conn.commit()
        conn.close()

        # 10. Show prediction result
        return render_template(
            "prediction.html",
            products=products,
            shipping_cost=shipping_cost,
            delivery_days=delivery_days
        )

    except ValueError as e:

        return render_template(
            "prediction.html",
            products=products,
            error=str(e)
        )

    except requests.RequestException:

        return render_template(
            "prediction.html",
            products=products,
            error="Road distance service is unavailable. Please try again."
        )

    except Exception as e:

        app.logger.exception("Prediction failed")

        return render_template(
            "prediction.html",
            products=products,
            error="Prediction failed. Please check your model and database configuration."
        )


@app.route("/history")
def history():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database/giftmedaily.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT product_name,
        product_value,
        destination_pin,
        weight,
        shipping_cost,
        delivery_days,
        prediction_date
    FROM prediction_history
    WHERE username=?
    ORDER BY id DESC
    """, (session["user"],))

    records = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        records=records
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=False)