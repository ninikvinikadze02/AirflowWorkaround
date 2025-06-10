from typing import Dict, Any

class GraphQLQueries:
    # Orders query with pagination
    ORDERS_QUERY = """
    query getOrders($query: String, $cursor: String) {
        orders(first: 250, after: $cursor, query: $query) {
            pageInfo {
                hasNextPage
                endCursor
            }
            edges {
                node {
                    id
                    name
                    createdAt
                    totalPriceSet {
                        shopMoney {
                            amount
                            currencyCode
                        }
                    }
                    customer {
                        firstName
                        lastName
                        email
                    }
                    lineItems(first: 50) {
                        edges {
                            node {
                                title
                                quantity
                                variant {
                                    price
                                    sku
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    # Products query with pagination
    PRODUCTS_QUERY = """
    query getProducts($query: String, $cursor: String) {
        products(first: 250, after: $cursor, query: $query) {
            pageInfo {
                hasNextPage
                endCursor
            }
            edges {
                node {
                    id
                    title
                    description
                    createdAt
                    variants(first: 50) {
                        edges {
                            node {
                                id
                                sku
                                price
                                inventoryQuantity
                            }
                        }
                    }
                }
            }
        }
    }
    """

    # Inventory query with pagination
    INVENTORY_QUERY = """
    query getInventoryLevels($query: String, $cursor: String) {
        inventoryItems(first: 250, after: $cursor, query: $query) {
            pageInfo {
                hasNextPage
                endCursor
            }
            edges {
                node {
                    id
                    sku
                    inventoryLevels(first: 1) {
                        edges {
                            node {
                                available
                                location {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    # Query mappings for different report types
    QUERY_MAPPINGS: Dict[str, Dict[str, Any]] = {
        'orders': {
            'query': ORDERS_QUERY,
            'data_path': ['data', 'orders', 'edges'],
            'page_info_path': ['data', 'orders', 'pageInfo'],
            'date_field': 'created_at'
        },
        'products': {
            'query': PRODUCTS_QUERY,
            'data_path': ['data', 'products', 'edges'],
            'page_info_path': ['data', 'products', 'pageInfo'],
            'date_field': 'created_at'
        },
        'inventory': {
            'query': INVENTORY_QUERY,
            'data_path': ['data', 'inventoryItems', 'edges'],
            'page_info_path': ['data', 'inventoryItems', 'pageInfo'],
            'date_field': 'updated_at'
        }
    }

    @classmethod
    def get_query_config(cls, report_type: str) -> Dict[str, Any]:
        """Get query configuration for a specific report type"""
        if report_type not in cls.QUERY_MAPPINGS:
            raise ValueError(f"Unknown report type: {report_type}")
        return cls.QUERY_MAPPINGS[report_type]

    @classmethod
    def get_date_filter(cls, report_type: str, date: str) -> str:
        """Generate date filter for a specific report type"""
        config = cls.get_query_config(report_type)
        date_field = config['date_field']
        return f'{date_field}:>="{date}"' 