FROM apache/airflow:2.8.0-python3.10

COPY requirements.txt /requirements.txt

USER airflow
RUN pip install --user --no-cache-dir -r /requirements.txt
