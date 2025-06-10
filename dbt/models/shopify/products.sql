{{
    config(
        materialized='table'
    )
}}

with products as (
    select
        node.id as product_id,
        node.title as product_title,
        node.description as product_description,
        node.createdAt as created_at,
        current_timestamp as loaded_at
    from {{ source('raw', 'shopify_products') }}
),

variants as (
    select
        node.id as product_id,
        jsonb_array_elements(node.variants.edges) as variant_edge
    from {{ source('raw', 'shopify_products') }}
),

product_variants as (
    select
        product_id,
        variant_edge->>'node' as variant_data
    from variants
)

select 
    p.*,
    pv.variant_data
from products p
left join product_variants pv on p.product_id = pv.product_id 