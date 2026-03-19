# Chicago Air Quality Monitoring System — Version 2
[Project Link](https://chicagoairqualityprediction.vercel.app/)
(It can take upto 40s to connect to mongodb since it is deployed on free instance of vercel)

This repository contains the updated, **end-to-end implementation** of a Chicago air quality monitoring and prediction system.  
The project was originally built as a frontend-only visualization tool (V1).  
**Version 2** expands it into a full **data engineering and machine learning pipeline**.

---

## 📊 Overview of V1 (Previous Version)

**Repository:** [https://github.com/Tilak2203/Chicago-air-quality-vercel](https://github.com/Tilak2203/Chicago-air-quality-vercel)

The earlier version (V1) consisted of:

- A React application
- Direct API calls to fetch parameter readings
- Basic data visualization
- No automated data pipeline
- No stored history
- 
---

## 🚀 Overview of V2 (Current Version)

Version 2 transitions the project to a **proper end-to-end pipeline**.  
It separates ingestion, processing, storage, prediction, API serving, and frontend visualization into **independent components**.

### Key Changes:

- Added **Airflow ETL pipeline** for scheduled data ingestion and cleaning
- **MongoDB Atlas** as the primary database
- Implemented a **machine learning model (RandomForest)** for PM2.5 forecasting
- Rebuilt the frontend to use backend APIs instead of direct external calls
- Centralized timestamp handling and preprocessing
- Organized the project into a **modular, production-style structure**

---

## 📁 Project Structure

```
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
```

---

## 🏗️ Architecture Summary

The system now follows a **straightforward pipeline**:

1. **Airflow** fetches air quality parameters data on a schedule, cleans it, normalizes timestamps, removes duplicates, and loads it into MongoDB.

2. **MongoDB Atlas** stores historical and latest readings.

3. **The Python backend** exposes REST endpoints for:
   - All cleaned readings
   - Prediction results
   - Prediction history
   - Model performance metrics

4. A **RandomForest model** provides next-hour PM2.5 predictions.

5. **The React frontend** consumes backend APIs, visualizes trends, allows date filtering, and displays predictions.

This mirrors a standard data engineering workflow:  
**ingest → clean → store → predict → serve → visualize**

---

## 🛠️ Running the System Locally

### 1. Start Airflow

```bash
cd airflow-docker
docker compose up airflow-init
docker compose up -d
```

### 2. Start Backend

```bash
cd Chicago-air-quality-render
pip install -r requirements.txt
python app.py
```

### 3. Start Frontend

```bash
cd Chicago-air-quality-vercel
npm install
npm start
```

---

## 🎯 Purpose of V2

This version provides a more **realistic demonstration** of data engineering and machine learning concepts:

- Automated, repeatable ingestion
- Centralized cloud database
- A reusable API layer
- Prediction workflows
- A clean separation between ETL, backend, and frontend

The system is **maintainable, extendable, and reflects real-world architecture**.

---
<img width="1782" height="958" alt="Screenshot 2026-01-12 at 11 47 48 AM" src="https://github.com/user-attachments/assets/a7ada997-8e00-4911-91b6-04474c0b0513" />


<img width="3124" height="1412" alt="image" src="https://github.com/user-attachments/assets/c667ee2d-3a10-4f67-ab37-c2a38dd3c118" />


