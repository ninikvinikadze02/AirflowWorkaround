{{
    config(
        materialized='table'
    )
}}

with inventory as (
    select
        node.id as inventory_item_id,
        node.sku as sku,
        jsonb_array_elements(node.inventoryLevels.edges) as inventory_level_edge
    from {{ source('raw', 'shopify_inventory') }}
),

inventory_levels as (
    select
        inventory_item_id,
        sku,
        inventory_level_edge->>'node' as inventory_level_data
    from inventory
)

select 
    inventory_item_id,
    sku,
    inventory_level_data->>'available' as available_quantity,
    inventory_level_data->'location'->>'name' as location_name,
    current_timestamp as loaded_at
from inventory_levels 