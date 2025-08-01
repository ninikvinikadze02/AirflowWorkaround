#!/bin/bash

echo "Setting up Shopify Pipeline..."

# Create necessary directories
mkdir -p logs
mkdir -p config

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Shopify API Configuration

# Database Configuration
EOF
    echo "Please update .env file with your Shopify credentials"
fi

# Start services
echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 60

# Initialize Airflow database
echo "Initializing Airflow database..."
docker-compose exec airflow-webserver airflow db init

# Create Airflow user
echo "Creating Airflow user..."
docker-compose exec airflow-webserver airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow

# Set up Airflow connections
echo "Setting up Airflow connections..."
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
    --conn-host 'nini-testing-store.myshopify.com' \
    --conn-password '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'

echo "Setup complete!"
echo "Please update the Shopify connection in Airflow UI with your actual credentials"
echo "Access Airflow UI at: http://localhost:8081"
echo "Username: airflow, Password: airflow" 