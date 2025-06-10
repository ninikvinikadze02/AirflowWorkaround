{{
    config(
        materialized='table'
    )
}}

with orders as (
    select
        node.id as order_id,
        node.name as order_name,
        node.createdAt as created_at,
        node.totalPriceSet.shopMoney.amount as total_amount,
        node.totalPriceSet.shopMoney.currencyCode as currency_code,
        node.customer.firstName as customer_first_name,
        node.customer.lastName as customer_last_name,
        node.customer.email as customer_email,
        current_timestamp as loaded_at
    from {{ source('raw', 'shopify_orders') }}
)

select * from orders 