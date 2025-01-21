# cng-python

A collection of some commonly used cloud-native geo utility functions for our python-based workflows


## Install


```python
pip install git+https://github.com/boettiger-lab/cng-python.git
```

## Utilities


 - `set_secrets()` Helper utility to read/write from S3 buckets. Particularly convenient for working with local minio buckets on Cirrus. duckdb S3 can read but not write to data.source.coop S3 at this time.


- Some pydeck helpers, from gbif hex maps
- H3 helper builtins (also used with gbif)
- leafmap/maplibre helper for terrain style  

