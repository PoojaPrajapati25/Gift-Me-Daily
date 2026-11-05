Gift Me Daily – Smart Shipping Cost & Delivery Time Prediction System

A Machine Learning-based web application that predicts estimated shipping charges and delivery time using shipment details and geographical information.

Project Overview

Gift Me Daily is a Flask-based web application developed to estimate shipping costs and expected delivery duration for shipments.

The system uses historical shipment data and two separate Machine Learning regression models to generate predictions. It also calculates road distance using the Open Source Routing Machine (OSRM) and displays prediction statistics through an interactive dashboard.

The main objective is to make shipping cost and delivery time estimation faster and more convenient.

Key Features

- Shipping Cost Prediction: Estimates shipping charges using a trained Machine Learning model.
- Delivery Time Prediction: Estimates the expected number of delivery days.
- PIN Code-Based Location: Uses destination PIN codes to retrieve geographical coordinates.
- Road Distance Calculation: Uses OSRM to calculate road-network distance from the fixed source location.
- User Login: Provides a login-protected application interface.
- Interactive Dashboard: Displays prediction statistics and charts.
- Prediction History: Stores previous predictions in an SQLite database.
- Data Visualization: Displays shipping cost comparisons, delivery-time trends, and product distribution.

Machine Learning Approach

The project uses two separate Random Forest Regression models.

| Model | Prediction Target |
|---|---|
| Shipping Cost Model | Shipping Charges |
| Delivery Time Model | Delivery Days |

Input Details

The prediction form accepts:

- Product Name
- Product Value
- Product Weight
- Destination PIN Code

The application processes the input, retrieves destination coordinates, calculates road distance, and prepares the required features in the same order used during model training.

Prediction Outputs

- Estimated Shipping Cost
- Estimated Delivery Time in Days

The predictions are estimates based on historical shipment patterns. They are not guaranteed actual shipping charges or delivery dates.

Geographical Enrichment

The application uses geographical information to improve shipment-related predictions.

1. Destination PIN codes are mapped to latitude and longitude coordinates.
2. The source location is fixed at PIN code `324007`.
3. OSRM is used to calculate road distance between the source and destination coordinates.
4. The calculated road distance is supplied to the Machine Learning models.

Note:Road-distance calculation depends on the availability and accuracy of geographical coordinates and the OSRM routing service.

Application Workflow

1. The user opens the web application.
2. The user logs in.
3. The dashboard displays prediction statistics.
4. The user enters shipment details on the prediction page.
5. The Flask backend validates the input.
6. Destination coordinates are retrieved using the PIN code.
7. Road distance is calculated using OSRM.
8. The trained models generate shipping cost and delivery-time predictions.
9. The prediction is saved in the SQLite database.
10. The user can view previous predictions in the history section.

Dashboard

The dashboard provides an overview of recorded prediction activity.

It includes:

- Total number of predictions
- Average shipping cost
- Average delivery time
- Most predicted product
- Shipping cost bar chart
- Delivery time line chart
- Product distribution pie chart

Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Web application backend |
| Pandas & NumPy | Data processing |
| Scikit-learn | Machine Learning |
| Random Forest Regressor | Prediction models |
| Joblib | Saving and loading trained models |
| SQLite | Prediction history storage |
| HTML & CSS | Frontend structure and styling |
| Bootstrap | Responsive user interface |
| JavaScript | Frontend interactions |
| Chart.js | Dashboard visualizations |
| OSRM | Road-distance calculation |
| AWS Elastic Beanstalk | Cloud deployment |

Project Structure

```text
Gift-Me-Daily/
│
├── app.py
├── database.py
├── view_database.py
├── requirements.txt
├── Procfile
├── README.md
├── .gitignore
├── .env.example
│
├── models/
│   ├── shipping_model.pkl
│   ├── delivery_model.pkl
│   ├── product_encoder.pkl
│   ├── feature_columns.pkl
│   └── pin_coordinates.pkl
│
├── dataset/
│   ├── Project.xlsx
│   └── India_PIN_Coordinates.csv
│
├── notebooks/
│   └── internship_project.ipynb
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── dashboard.html
│   ├── prediction.html
│   └── history.html
│
└── static/
    └── style.css
```

*The structure above is the intended project layout. Include only the files and folders that are actually present in your repository.*

Installation and Setup

Follow these steps to run the project locally.

1. Clone the Repository

```bash
git clone https://github.com/PoojaPrajapati25/Gift-Me-Daily.git
```

2. Navigate to the Project Folder

```bash
cd Gift-Me-Daily
```

3. Create a Virtual Environment

```bash
python -m venv venv
```

4. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

5. Install Dependencies

```bash
pip install -r requirements.txt
```

6. Configure the Secret Key

Set the Flask secret key as an environment variable.

For Windows PowerShell:

```powershell
$env:SECRET_KEY = "your-generated-secret-key"
```

Use a securely generated secret key rather than a sample value in an actual deployment.

7. Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

Make sure the required model files, database setup, and configuration are available before running the application.

Database

The application uses SQLite to store prediction history.

The stored prediction details include:

- Username
- Product name
- Product value
- Destination PIN code
- Weight
- Predicted shipping cost
- Predicted delivery days
- Prediction date

Deployment

The project includes a `Procfile` configured to run the Flask application using Gunicorn and is intended for deployment on AWS Elastic Beanstalk.

The deployment environment must have the required Python dependencies, model files, database configuration, and `SECRET_KEY` environment variable.

Current Limitations

- Prediction accuracy depends on the quality and quantity of historical shipment data.
- Actual shipping charges and delivery duration may vary due to operational conditions.
- OSRM routing availability affects road-distance calculation.
- The application provides model-based estimates and does not provide live courier tracking.
- New predictions are stored in the database, but the trained models do not automatically learn or retrain from those predictions.

Future Enhancements

- Collect actual shipment outcomes for model validation.
- Periodically retrain models using verified new shipment records.
- Integrate live courier tracking APIs.
- Expand the historical shipment dataset.
- Improve prediction accuracy with additional relevant features.
- Use a persistent production database for cloud deployment.

Project Objective

The project demonstrates how Machine Learning, geographical data, and Flask web development can be combined to build a practical shipping prediction application.

It aims to simplify shipping cost estimation and provide expected delivery-time information through an interactive web interface.

---

**Developed as an Academic Machine Learning Project**