import boto3
import pandas as pd
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.hooks.base import BaseHook
from airflow.models import Variable

class S3Operator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        aws_conn_id: str = 'aws_default',
        bucket_name: str = None,
        postgres_conn_id: str = 'postgres_default',
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.aws_conn_id = aws_conn_id
        self.bucket_name = bucket_name or Variable.get('s3_bucket_name')
        self.postgres_conn_id = postgres_conn_id

    def execute(self, context):
        # Get AWS credentials from Airflow connection
        aws_conn = BaseHook.get_connection(self.aws_conn_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_conn.login,
            aws_secret_access_key=aws_conn.password
        )

        # List objects in bucket
        response = s3_client.list_objects_v2(Bucket=self.bucket_name)
        
        # Extract file information
        file_data = []
        for obj in response.get('Contents', []):
            file_data.append({
                'file_name': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'],
                'storage_class': obj['StorageClass']
            })

        # Convert to DataFrame
        df = pd.DataFrame(file_data)

        # Save to PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        engine = pg_hook.get_sqlalchemy_engine()
        
        df.to_sql(
            's3_files',
            engine,
            if_exists='replace',
            index=False
        ) 