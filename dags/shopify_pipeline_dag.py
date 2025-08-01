from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable

from plugins.shopify_operator import ShopifyOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'shopify_pipeline',
    default_args=default_args,
    description='Shopify data pipeline: Extract raw data and transform with dbt',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['shopify', 'data_pipeline'],
) as dag:

    # Create raw_shopify schema if it doesn't exist
    create_schema = PostgresOperator(
        task_id='create_raw_schema',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE SCHEMA IF NOT EXISTS raw_shopify;
        CREATE SCHEMA IF NOT EXISTS shopify_analytics;
        """
    )

    # Shopify data extraction
    shopify_extract = ShopifyOperator(
        task_id='shopify_extract',
        shopify_conn_id='shopify_default',
        postgres_conn_id='postgres_default',
        days_back=2,
        max_workers=5
    )

    # dbt transformation for Shopify models only
    dbt_run_shopify = BashOperator(
        task_id='dbt_run_shopify',
        bash_command='cd /opt/airflow/dbt && dbt run --select shopify',
        cwd='/opt/airflow/dbt'
    )

    # Set task dependencies
    create_schema >> shopify_extract >> dbt_run_shopify 