import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.hooks.base import BaseHook

class SpotifyOperator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        spotify_conn_id: str = 'spotify_default',
        postgres_conn_id: str = 'postgres_default',
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.spotify_conn_id = spotify_conn_id
        self.postgres_conn_id = postgres_conn_id

    def execute(self, context):
        # Get Spotify credentials from Airflow connection
        spotify_conn = BaseHook.get_connection(self.spotify_conn_id)
        
        # Initialize Spotify client
        client_credentials_manager = SpotifyClientCredentials(
            client_id=spotify_conn.login,
            client_secret=spotify_conn.password
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Get your playlists
        playlists = sp.current_user_playlists()
        
        # Extract playlist data
        playlist_data = []
        for playlist in playlists['items']:
            playlist_data.append({
                'playlist_id': playlist['id'],
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'tracks_count': playlist['tracks']['total'],
                'owner': playlist['owner']['display_name']
            })

        # Convert to DataFrame
        df = pd.DataFrame(playlist_data)

        # Save to PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        engine = pg_hook.get_sqlalchemy_engine()
        
        df.to_sql(
            'spotify_playlists',
            engine,
            if_exists='replace',
            index=False
        ) 