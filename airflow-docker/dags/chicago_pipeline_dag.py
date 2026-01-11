from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Import actual functions that exist

from scripts.extract_openaq import extract_data
from scripts.transform_data import transform_data
from scripts.load_to_mongo import load_to_mongo
from scripts.run_model import run_model


default_args = {
    "owner": "tilak",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="chicago_air_quality_pipeline",
    description="Real-time air quality ETL + prediction pipeline for Chicago",
    start_date=datetime(2024, 1, 1),
    schedule_interval="20 * * * *",  
    catchup=False,
    default_args=default_args,
) as dag:

    extract_task = PythonOperator(
    task_id="extract_openaq_data",
    python_callable=extract_data
    )


    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )

    load_task = PythonOperator(
        task_id="load_mongodb",
        python_callable=load_to_mongo
    )

    # model_task = PythonOperator(
    #     task_id="predict_pm25",
    #     python_callable=run_model
    # )

    extract_task >> transform_task >> load_task 
