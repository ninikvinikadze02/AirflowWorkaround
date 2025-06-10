from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable

from plugins.shopify_operator import ShopifyOperator
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
    description='Pipeline for Shopify and S3 data ingestion',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['shopify', 's3', 'data_pipeline'],
) as dag:

    # Shopify data extraction
    shopify_extract = ShopifyOperator(
        task_id='shopify_extract',
        shopify_conn_id='shopify_default',
        postgres_conn_id='postgres_default',
        days_back=2,
        max_workers=5
    )

    # S3 data extraction
    s3_extract = S3Operator(
        task_id='s3_extract',
        aws_conn_id='aws_default',
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
    [shopify_extract, s3_extract] >> dbt_run 