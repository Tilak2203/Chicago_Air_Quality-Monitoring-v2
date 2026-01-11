Chicago Air Quality Monitoring System — Version 2

This repository contains the updated, end-to-end implementation of a Chicago air quality monitoring and prediction system.
The project was originally built as a frontend-only visualization tool (V1).
Version 2 expands it into a full data engineering and machine learning pipeline.

Overview of V1 (Previous Version)

Repository: https://github.com/Tilak2203/Chicago-air-quality-vercel

The earlier version (V1) consisted of:

A React application

Direct API calls to fetch PM2.5 readings

Basic data visualization

No automated data pipeline

No backend

No stored history

No machine learning predictions

This version worked but had several limitations:

Data was fetched only at runtime

No long-term storage or historical dataset

No ETL or cleaning

No prediction capability

The entire system existed only on the frontend

Overview of V2 (Current Version)

Version 2 transitions the project to a proper end-to-end pipeline.
It separates ingestion, processing, storage, prediction, API serving, and frontend visualization into independent components.

Key changes:

Added Airflow ETL pipeline for scheduled data ingestion and cleaning

Introduced MongoDB Atlas as the primary database

Added a Python backend to serve data and predictions through REST APIs

Implemented a machine learning model (RandomForest) for PM2.5 forecasting

Rebuilt the frontend to use backend APIs instead of direct external calls

Centralized timestamp handling and preprocessing

Organized the project into a modular, production-style structure

Project Structure
Chicago-Air-Quality-Monitoring-v2/
│
├── airflow-docker/                 # Airflow ETL pipeline (Dockerized)
│   ├── dags/
│   ├── docker-compose.yaml
│   └── requirements.txt
│
├── Chicago-air-quality-render/     # Python backend (API + ML)
│   ├── app.py
│   ├── mongodb.py
│   ├── predict.py
│   ├── utils.py
│   ├── model.pkl
│   └── requirements.txt
│
├── Chicago-air-quality-vercel/     # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
│
└── data/                           # Local CSV storage (optional)

Architecture Summary

The system now follows a straightforward pipeline:

Airflow fetches PM2.5 data on a schedule, cleans it, normalizes timestamps, removes duplicates, and loads it into MongoDB.

MongoDB Atlas stores historical and latest readings.

The Python backend exposes REST endpoints for:

all cleaned readings

prediction results

prediction history

model performance metrics

A RandomForest model provides next-hour PM2.5 predictions.

The React frontend consumes backend APIs, visualizes trends, allows date filtering, and displays predictions.

This mirrors a standard data engineering workflow: ingest → clean → store → predict → serve → visualize.

Running the System Locally
1. Start Airflow
cd airflow-docker
docker compose up airflow-init
docker compose up -d

2. Start Backend
cd Chicago-air-quality-render
pip install -r requirements.txt
python app.py


Backend runs at:
http://localhost:5000

3. Start Frontend
cd Chicago-air-quality-vercel
npm install
npm start


Frontend runs at:
http://localhost:3000

Version Comparison
Feature	V1	V2
Frontend	Yes	Yes (updated)
ETL Pipeline	No	Yes (Airflow)
Database	No	Yes (MongoDB Atlas)
Backend API	No	Yes
Machine Learning	No	Yes
Historical Storage	No	Yes
Automated Scheduling	No	Yes
Timestamp Cleaning	Basic	Robust
Purpose of V2

This version provides a more realistic demonstration of data engineering and machine learning concepts:

Automated, repeatable ingestion

Centralized cloud database

A reusable API layer

Prediction workflows

A clean separation between ETL, backend, and frontend

The system is maintainable, extendable, and reflects real-world architecture.
