{{
    config(
        materialized='table'
    )
}}

select
    file_name,
    size as file_size_bytes,
    last_modified as last_modified_at,
    storage_class,
    current_timestamp as loaded_at
from {{ source('raw', 's3_files') }} 