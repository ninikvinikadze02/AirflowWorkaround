from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable

from plugins.spotify_operator import SpotifyOperator
from plugins.s3_operator import S3Operator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'data_pipeline',
    default_args=default_args,
    description='Pipeline for Spotify and S3 data ingestion',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['spotify', 's3', 'data_pipeline'],
) as dag:

    # Spotify data extraction
    spotify_extract = SpotifyOperator(
        task_id='spotify_extract',
        spotify_client_id=Variable.get('spotify_client_id'),
        spotify_client_secret=Variable.get('spotify_client_secret'),
        postgres_conn_id='postgres_default'
    )

    # S3 data extraction
    s3_extract = S3Operator(
        task_id='s3_extract',
        aws_access_key_id=Variable.get('aws_access_key_id'),
        aws_secret_access_key=Variable.get('aws_secret_access_key'),
        bucket_name=Variable.get('s3_bucket_name'),
        postgres_conn_id='postgres_default'
    )

    # dbt transformation
    dbt_run = PostgresOperator(
        task_id='dbt_run',
        postgres_conn_id='postgres_default',
        sql='cd /opt/airflow/dbt && dbt run',
    )

    # Set task dependencies
    [spotify_extract, s3_extract] >> dbt_run 