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

@ibis.udf.scalar.builtin
def h3_cell_to_parent(int, int) -> int:
    ...

