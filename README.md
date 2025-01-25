# cng-python

A collection of some commonly used cloud-native geo utility functions for our python-based workflows


## Install


```python
pip install git+https://github.com/boettiger-lab/cng-python.git
```

## Utilities

- PMTiles writing:

Note that PMTiles cannot stream to/from remote sources, and that it does not understand parquet input (requires GeoJSON or flatgeobuf?).  
A few additional helpers for our common workflow to go from remote parquet and write pmtiles to a bucket:

```python
from cng.utils import to_geojson, to_pmtiles, s3_cp
parquet = 'https://minio.carlboettiger.info/public-biodiversity/pad-us-4/pad-us-4.parquet'
to_geojson(parquet, "pad-us-4.geojson")
pmtiles = to_pmtiles("pad-us-4.geojson", "pad-us-4.pmtiles")

# upload, since pmtiles cannot stream to/from buckets
s3_cp('pad-us-4.pmtiles', "s3://public-biodiversity/pad-us-4/pad-us-4.pmtiles", "minio")
```

Check out optional arguments for these functions.  In particular, note that `s3_cp()` uses Cirrus MINIO config by default but can copy to source.coop as well.  Note that `to_pmtiles()` includes configurable options!  e.g. if writing tiled polygons, like Census tracts, probably better to set `options=[]` so that no tracks are dropped (which creates holes).  Lastly, note `to_json` can take a connection.  

Make sure geometries are valid and in the desired projection (e.g. EPSG:4326) first.  


 - `set_secrets()` Helper utility to read/write from S3 buckets. Particularly convenient for working with local minio buckets on Cirrus. duckdb S3 can read but not write to data.source.coop S3 at this time.


- Some pydeck helpers, from gbif hex maps
- H3 helper builtins (also used with gbif)
- leafmap/maplibre helper for terrain style  

