# Shopify Pipeline Setup Guide

This guide will help you set up and run the Shopify data pipeline that extracts data from the Shopify API and transforms it using dbt.

## Pipeline Overview

The Shopify pipeline works as follows:

1. **Shopify Operator** extracts raw data from Shopify API (orders, products, inventory)
2. **Raw data** is stored in the `raw_shopify` schema in PostgreSQL
3. **dbt models** transform the raw data into analytics-ready tables in the `shopify_analytics` schema

## Prerequisites

- Docker and Docker Compose installed
- Shopify store with API access
- Shopify access token with appropriate permissions

## Quick Setup

### 1. Run the Setup Script

```bash
./setup_shopify_pipeline.sh
```

This script will:
- Create necessary directories
- Create a `.env` file template
- Build the custom Airflow image with dbt
- Start all services
- Initialize Airflow database and user
- Set up basic connections

### 2. Configure Shopify Credentials

Edit the `.env` file with your Shopify credentials:

```bash
# Shopify API Configuration
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_access_token
```

### 3. Update Airflow Connection

1. Open Airflow UI: http://localhost:8081
2. Login with: `airflow` / `airflow`
3. Go to Admin → Connections
4. Edit the `shopify_default` connection:
   - Host: `your-store.myshopify.com`
   - Password: `your_access_token`

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Environment File

```bash
cat > .env << EOF
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_access_token
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
EOF
```

### 2. Build and Start Services

```bash
# Build custom Airflow image
docker build -t custom-airflow:2.7.1 -f Dockerfile.airflow .

# Start services
docker-compose up -d

# Wait for services to be ready
sleep 45
```

### 3. Initialize Airflow

```bash
# Initialize database
docker-compose exec airflow-webserver airflow db init

# Create user
docker-compose exec airflow-webserver airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow

# Set up connections
docker-compose exec airflow-webserver airflow connections add \
    'postgres_default' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-schema 'airflow'

docker-compose exec airflow-webserver airflow connections add \
    'shopify_default' \
    --conn-type 'http' \
    --conn-host 'your-store.myshopify.com' \
    --conn-password 'your_access_token'
```

## Running the Pipeline

### 1. Enable the DAG

1. Open Airflow UI: http://localhost:8081
2. Find the `shopify_pipeline` DAG
3. Toggle it to "On" (unpause)

### 2. Trigger Manual Run

1. Click on the `shopify_pipeline` DAG
2. Click "Trigger DAG" button
3. Monitor the execution in the Graph view

### 3. Check Results

The pipeline will create:

**Raw Tables** (in `raw_shopify` schema):
- `shopify_orders` - Raw order data from API
- `shopify_products` - Raw product data from API  
- `shopify_inventory` - Raw inventory data from API

**Analytics Tables** (in `shopify_analytics` schema):
- `orders` - Transformed order data
- `products` - Transformed product data with variants
- `inventory` - Transformed inventory data with levels

## Pipeline Tasks

The `shopify_pipeline` DAG contains these tasks:

1. **create_raw_schema** - Creates `raw_shopify` and `shopify_analytics` schemas
2. **shopify_extract** - Extracts data from Shopify API (last 2 days by default)
3. **dbt_run_shopify** - Runs dbt transformations on Shopify models only

## Configuration Options

### Shopify Operator Parameters

- `days_back`: Number of days to look back for data (default: 2)
- `max_workers`: Number of parallel workers for API calls (default: 5)

### dbt Configuration

- **Profile**: `data_pipeline` (configured in `dbt/profiles.yml`)
- **Target Schema**: `shopify_analytics` (configured in `dbt/dbt_project.yml`)
- **Raw Schema**: `raw_shopify` (configured in `dbt/models/sources.yml`)

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check Shopify credentials in Airflow connections
2. **Schema Errors**: Ensure schemas are created before running dbt
3. **Permission Errors**: Verify Shopify access token has required permissions

### Logs

```bash
# View Airflow logs
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver

# View specific task logs in Airflow UI
```

### Testing dbt Locally

```bash
# Test dbt connection
docker-compose exec airflow-webserver bash -c "cd /opt/airflow/dbt && dbt debug"

# Run dbt models manually
docker-compose exec airflow-webserver bash -c "cd /opt/airflow/dbt && dbt run --select shopify"
```

## Data Flow

```
Shopify API → Shopify Operator → raw_shopify schema → dbt models → shopify_analytics schema
```

## Next Steps

Once the Shopify pipeline is working:

1. Add data quality tests to dbt models
2. Set up monitoring and alerting
3. Add more Shopify data types (customers, transactions, etc.)
4. Integrate with other data sources

## Files Structure

```
.
├── dags/
│   └── shopify_pipeline_dag.py          # Shopify-specific DAG
├── plugins/
│   ├── shopify_operator.py              # Shopify data extraction
│   └── graphql_queries.py               # Shopify GraphQL queries
├── dbt/
│   ├── models/
│   │   └── shopify/                     # dbt transformation models
│   ├── dbt_project.yml                  # dbt project configuration
│   ├── profiles.yml                     # Database connection config
│   └── models/sources.yml               # Source table definitions
├── docker-compose.yml                   # Service orchestration
├── Dockerfile.airflow                   # Custom Airflow image
├── setup_shopify_pipeline.sh            # Setup script
└── .env                                 # Environment variables
``` 