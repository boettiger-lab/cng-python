import os
import ibis



# DuckDB S3 authentication helpers
def set_secrets(con,
                key = os.getenv("MINIO_KEY", ""), 
                secret = os.getenv("MINIO_SECRET", ""), 
                endpoint = "minio.carlboettiger.info",
                bucket = '',
                url_style = "path"):
    
    if 'amazonaws.com' in endpoint:
        url_style = 'vhost'    

    if bucket != '':
        bucket = f"SCOPE 's3://{bucket}',"

    query = f'''
    CREATE OR REPLACE SECRET s3_{key} (
        TYPE S3,
        KEY_ID '{key}',
        SECRET '{secret}',
        ENDPOINT '{endpoint}',
        {bucket}
        URL_STYLE '{url_style}'
    );
    '''
    con.raw_sql(query)


def source_secrets(con, 
                   key = os.getenv("SOURCE_KEY", ""), 
                   secret = os.getenv("SOURCE_SECRET", ""),
                   endpoint = "data.source.coop",
                   bucket = "cboettig"):
    set_secrets(con, key, secret, endpoint = endpoint, bucket = bucket)


## kinda silly wraper to minio.Minio but provides my defaults.  Sadly also not working with source.coop yet
import minio
def s3_client(key = os.getenv("MINIO_KEY", ""), 
              secret = os.getenv("MINIO_SECRET", ""), 
              endpoint = "minio.carlboettiger.info"
             ):
    return minio.Minio(endpoint, key, secret)

# Define H3 builtins for DuckDB

# make sure h3 is installed.
def duckdb_install_h3(): 
    import duckdb
    db = duckdb.connect()
    db.install_extension("h3", repository = "community")
    db.close()



## DeckGL layer, for pydeck or maplibre 
import pydeck as pdk
def HexagonLayer(data, v_scale = 1):
    return pdk.Layer(
            "H3HexagonLayer",
            id="gbif",
            data=data,
            extruded=True,
            get_elevation="value",
            get_hexagon="hex",
            elevation_scale = 50 * v_scale,
            elevation_range = [0,1],
            pickable=True,
            auto_highlight=True,
            get_fill_color="[255 - value, 255, value]",
            )

# Pure pydeck, not compatible with maplibre yet
def DeckGlobe(layer):
    view_state = pdk.ViewState(latitude=51.47, longitude=0.45, zoom=0)
    view = pdk.View(type="_GlobeView", controller=True, width=1000, height=600)
    COUNTRIES = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson"
    
    layers = [
        pdk.Layer(
            "GeoJsonLayer",
            id="base-map",
            data=COUNTRIES,
            stroked=False,
            filled=True,
            get_fill_color=[200, 200, 200],
        ),
        layer,
    ]
    deck = pdk.Deck(
        views=[view],
        initial_view_state=view_state,
        layers=layers,
        map_provider=None,
        # Note that this must be set for the globe to be opaque
        parameters={"cull": True},
    )
    return deck




def terrain_style(key = os.getenv('MAPTILER_KEY'), exaggeration = 1):
    return {
        "version": 8,
        "sources": {
            "osm": {
                "type": "raster",
                "tiles": ["https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}.png"],
                "tileSize": 256,
                "attribution": "&copy; National Geographic",
                "maxzoom": 19,
            },
            "terrainSource": {
                "type": "raster-dem",
                "url": f"https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key={key}",
                "tileSize": 256,
            },
            "hillshadeSource": {
                "type": "raster-dem",
                "url": f"https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key={key}",
                "tileSize": 256,
            },
        },
        "layers": [
            {"id": "osm", "type": "raster", "source": "osm"},
            {
                "id": "hills",
                "type": "hillshade",
                "source": "hillshadeSource",
                "layout": {"visibility": "visible"},
                "paint": {"hillshade-shadow-color": "#473B24"},
            },
        ],
        "terrain": {"source": "terrainSource", "exaggeration": exaggeration},
    }
    



# enable ibis to use built-in function from the h3 extension

@ibis.udf.scalar.builtin
def h3_cell_to_boundary_wkt	(array) -> str:
    ...

@ibis.udf.scalar.builtin
def h3_latlng_to_cell(lat: float, lng: float, zoom: int) -> int:
    ...
@ibis.udf.scalar.builtin
def hex(array) -> str:
    ...

