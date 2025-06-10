{{
    config(
        materialized='table'
    )
}}

select
    playlist_id,
    name as playlist_name,
    description as playlist_description,
    tracks_count,
    owner as playlist_owner,
    current_timestamp as loaded_at
from {{ source('raw', 'spotify_playlists') }} 