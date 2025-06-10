import os
import json
import requests
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Dict, List, Any, Optional
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.hooks.base import BaseHook
from graphql_queries import GraphQLQueries

class ShopifyOperator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        shopify_conn_id: str = 'shopify_default',
        postgres_conn_id: str = 'postgres_default',
        days_back: int = 2,
        max_workers: int = 5,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.shopify_conn_id = shopify_conn_id
        self.postgres_conn_id = postgres_conn_id
        self.days_back = days_back
        self.max_workers = max_workers

    def execute(self, context):
        # Get Shopify credentials from Airflow connection
        shopify_conn = BaseHook.get_connection(self.shopify_conn_id)
        
        # Initialize Shopify client
        client = ShopifyGraphQLClient(
            store_url=shopify_conn.host,
            access_token=shopify_conn.password,
            max_workers=self.max_workers
        )
        
        # Fetch data
        results = client.fetch_all_data_parallel(days_back=self.days_back)
        
        # Process and save each data type
        pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        engine = pg_hook.get_sqlalchemy_engine()
        
        for data_type, data in results.items():
            # Convert to DataFrame
            df = pd.json_normalize(data)
            
            # Save to PostgreSQL
            table_name = f'shopify_{data_type}'
            df.to_sql(
                table_name,
                engine,
                if_exists='replace',
                index=False
            )
            
            self.log.info(f"Saved {len(data)} {data_type} records to {table_name}")

class ShopifyGraphQLClient:
    def __init__(self, store_url: str, access_token: str, max_workers: int = 5):
        self.store_url = store_url
        self.access_token = access_token
        self.api_version = '2024-01'
        self.base_url = f'https://{self.store_url}/admin/api/{self.api_version}/graphql.json'
        self.headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json',
        }
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={'query': query, 'variables': variables}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error executing query: {e}")
            return None

    def get_nested_value(self, data: Dict, path: List[str]) -> Any:
        current = data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def fetch_paginated_data(self, report_type: str, days_back: Optional[int] = None) -> List[Dict]:
        config = GraphQLQueries.get_query_config(report_type)
        query = config['query']
        data_path = config['data_path']
        page_info_path = config['page_info_path']

        date_filter = ""
        if days_back:
            date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            date_filter = GraphQLQueries.get_date_filter(report_type, date)

        def fetch_page(cursor: Optional[str] = None) -> Dict:
            variables = {
                "query": date_filter,
                "cursor": cursor
            }
            return self.execute_query(query, variables)

        first_page = fetch_page()
        if not first_page:
            return []

        all_items = []
        page_info = self.get_nested_value(first_page, page_info_path)
        if not page_info:
            return []

        has_next_page = page_info['hasNextPage']
        cursor = page_info['endCursor']
        
        items = self.get_nested_value(first_page, data_path)
        if items:
            all_items.extend(items)

        futures = []
        while has_next_page:
            futures.append(self.executor.submit(fetch_page, cursor))
            if len(futures) >= self.max_workers:
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        items = self.get_nested_value(result, data_path)
                        if items:
                            all_items.extend(items)
                        page_info = self.get_nested_value(result, page_info_path)
                        if page_info:
                            has_next_page = page_info['hasNextPage']
                            cursor = page_info['endCursor']
                futures = []

        for future in as_completed(futures):
            result = future.result()
            if result:
                items = self.get_nested_value(result, data_path)
                if items:
                    all_items.extend(items)

        return all_items

    def fetch_all_data_parallel(self, days_back: Optional[int] = None) -> Dict[str, List[Dict]]:
        start_time = time.time()
        
        futures = {
            self.executor.submit(self.fetch_paginated_data, 'orders', days_back): "orders",
            self.executor.submit(self.fetch_paginated_data, 'products', days_back): "products",
            self.executor.submit(self.fetch_paginated_data, 'inventory', days_back): "inventory"
        }
        
        results = {}
        
        for future in as_completed(futures):
            data_type = futures[future]
            try:
                data = future.result()
                results[data_type] = data
                print(f"Completed fetching {data_type}: {len(data)} items")
            except Exception as e:
                print(f"Error fetching {data_type}: {e}")
        
        end_time = time.time()
        print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
        
        return results

    def __del__(self):
        self.executor.shutdown(wait=False) 