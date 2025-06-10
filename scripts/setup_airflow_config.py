from airflow.models import Variable, Connection
from airflow import settings
import os
from dotenv import load_dotenv

def setup_airflow_config():
    # Load environment variables from .env file
    load_dotenv()
    
    # Set up Variables
    Variable.set("spotify_client_id", os.getenv("SPOTIFY_CLIENT_ID"))
    Variable.set("spotify_client_secret", os.getenv("SPOTIFY_CLIENT_SECRET"))
    Variable.set("s3_bucket_name", os.getenv("S3_BUCKET_NAME"))
    
    # Set up Connections
    session = settings.Session()
    
    # Spotify connection
    spotify_conn = Connection(
        conn_id='spotify_default',
        conn_type='spotify',
        login=os.getenv("SPOTIFY_CLIENT_ID"),
        password=os.getenv("SPOTIFY_CLIENT_SECRET")
    )
    
    # AWS connection
    aws_conn = Connection(
        conn_id='aws_default',
        conn_type='aws',
        login=os.getenv("AWS_ACCESS_KEY_ID"),
        password=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    # Add connections if they don't exist
    if not session.query(Connection).filter(Connection.conn_id == spotify_conn.conn_id).first():
        session.add(spotify_conn)
    
    if not session.query(Connection).filter(Connection.conn_id == aws_conn.conn_id).first():
        session.add(aws_conn)
    
    session.commit()
    session.close()

if __name__ == "__main__":
    setup_airflow_config() 