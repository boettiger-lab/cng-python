import os
import ibis

# pydeck-based helpers

# also see utils.to_geojson for path-based method

# FIXME define as a method for an ibis table instead of a function
def to_json (df, path, con):
  query = ibis.to_sql(df)
  con.raw_sql(f"COPY ({query}) TO '{path}' (FORMAT JSON, ARRAY true);")


## DeckGL layer, for pydeck or maplibre 
import pydeck as pdk
def HexagonLayer(data, v_scale = 1, hexagon = "h3id", value = "value", fill = "[255 - value, 255, value]"):
    return pdk.Layer(
            "H3HexagonLayer",
            id="data",
            data=data,
            extruded=True,
            get_elevation=value,
            get_hexagon=hexagon,
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



# Leafmap / MapLibre style

# Note: MAPTILER_KEY is free (up to certain rate-limit)
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
