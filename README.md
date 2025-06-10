# Data Pipeline Project

This project implements a data pipeline using Apache Airflow, dbt, and PostgreSQL to extract data from Spotify and AWS S3, transform it, and load it into a PostgreSQL database.

## Project Structure

```
.
├── dags/                    # Airflow DAGs
│   └── data_pipeline_dag.py
├── plugins/                 # Custom Airflow operators
│   ├── spotify_operator.py
│   └── s3_operator.py
├── dbt/                     # dbt project
│   ├── models/
│   │   ├── spotify/
│   │   └── s3/
│   ├── dbt_project.yml
│   └── profiles.yml
├── docker-compose.yml       # Docker configuration
└── requirements.txt         # Python dependencies
```

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file with the following variables:
     ```
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret
     AWS_ACCESS_KEY_ID=your_aws_access_key
     AWS_SECRET_ACCESS_KEY=your_aws_secret_key
     S3_BUCKET_NAME=your_bucket_name
     ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access Airflow UI:
   - Open http://localhost:8080
   - Default credentials: airflow/airflow

## Pipeline Components

1. **Spotify Data Extraction**
   - Extracts playlist information from Spotify API
   - Stores data in PostgreSQL

2. **S3 Data Extraction**
   - Lists objects in specified S3 bucket
   - Stores file metadata in PostgreSQL

3. **dbt Transformations**
   - Transforms raw data into analytics-ready tables
   - Implements data quality tests

## Adding New Data Sources

To add a new data source:

1. Create a new custom operator in the `plugins/` directory
2. Add the operator to the DAG in `dags/data_pipeline_dag.py`
3. Create corresponding dbt models in `dbt/models/`

## Development

- Airflow DAGs are automatically loaded from the `dags/` directory
- dbt models can be tested locally using `dbt run`
- Use `docker-compose logs` to view service logs 