import os
import ibis
import subprocess
import re


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


# define these as chainable methods?

def to_geojson(input_file, 
               output_file = "/tmp/tmp.geojson", 
               con = ibis.duckdb.connect(extensions=["spatial"])):

    # accept a path and create a ibis table:
    if not isinstance(input_file, ibis.expr.types.relations.Table):
          input_file = con.read_parquet(input_file)
    
    query = ibis.to_sql(input_file)
    con.raw_sql(f'''
      COPY ({query}) TO '{output_file}' 
      WITH (FORMAT GDAL, DRIVER 'GeoJSON', LAYER_CREATION_OPTIONS 'WRITE_BBOX=YES');
    ''')
    return(output_file)


def to_pmtiles(input_file, 
               output_file = None, 
               max_zoom = 12,
               overwrite = True,
               options = ["--drop-densest-as-needed", "--extend-zooms-if-still-dropping"]

):
    # check or convert to local geojson?
    # check crs?
    # check valid?

    if output_file is None:
        output_file = re.sub(r"\..+$", ".pmtiles", input_file)

    # Ensure Tippecanoe is installed
    if subprocess.call(["which", "tippecanoe"], stdout=subprocess.DEVNULL) != 0:
        raise RuntimeError("Tippecanoe is not installed or not in PATH")

    # Construct the Tippecanoe command
    command = [
        "tippecanoe",
        "-o", output_file,
        "-z", str(max_zoom)]

    command.extend(options)

    if overwrite:
        command.extend(["--force"])

    command.extend([input_file])

    # Run Tippecanoe
    try:
        subprocess.run(command, check=True)
        print(f"Successfully generated PMTiles file: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error running Tippecanoe: {e}")
    
    return(output_file)


# kinda silly.  boto3 doesn't do sync, maybe we just awscli wrap
# would be nice if source.coop supported minio client library
import boto3
from botocore.client import Config
import streamlit as st
def s3_cp(source, 
          dest, 
          profile = "minio",
          key = "", #st.secrets["MINIO_KEY"],
          secret = "", #st.secrets["MINIO_SECRET"]
          ):

    # assume dest is an s3_path?
    match = re.match(r'^s3://([^/]+)/(.*)$', dest)
    bucket, object_name = match.groups()
    if profile == "minio":
        s3 = boto3.client(
            "s3",
            endpoint_url = "https://minio.carlboettiger.info",
            aws_access_key_id = os.getenv("MINIO_KEY", key), 
            aws_secret_access_key = os.getenv("MINIO_SECRET", secret),
            config=Config(s3={'addressing_style': 'path'})
        )
        s3.upload_file(source, bucket, object_name)
    if profile == "sc":
        s3 = boto3.client("s3",
            endpoint_url = "https://data.source.coop",
            aws_access_key_id = os.getenv("SOURCE_KEY", key), 
            aws_secret_access_key = os.getenv("SOURCE_SECRET", secret),
            config=Config(s3={'addressing_style': 'path', 
                              'multipart_threshold': '44MB'})
        )
    s3.upload_file(source, bucket, object_name)
    



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

# upload file to huggingface
from huggingface_hub import HfApi, login
def hf_upload(file, path, repo_id = "boettiger-lab/ca-30x30", repo_type = "dataset", key = None):
    if not key:
        key = st.secrets["HF_TOKEN"]
    login(key)
    api = HfApi()
    info = api.upload_file(
            path_or_fileobj=path,
            path_in_repo=file,
            repo_id=repo_id,
            repo_type=repo_type, 
        )
        
# enable ibis to use built-in function from the h3 extension

@ibis.udf.scalar.builtin
def h3_polygon_wkt_to_cells_string (geom, int) -> str:
    ...

import ibis.expr.datatypes as dt
# usage: t.mutate(geom_valid = ST_MakeValid(t.geom))
@ibis.udf.scalar.builtin
def ST_MakeValid(geom) -> dt.geometry:
    ...

@ibis.udf.scalar.builtin
def h3_cell_to_boundary_wkt	(array) -> str:
    ...

@ibis.udf.scalar.builtin
def h3_latlng_to_cell(lat: float, lng: float, zoom: int) -> int:
    ...
@ibis.udf.scalar.builtin
def hex(array) -> str:
    ...




