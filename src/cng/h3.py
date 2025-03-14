# enable ibis to use built-in function from the h3 extension
import ibis

def to_h3j (df, path):

    con = df._find_backend() # df.get_backend() ibis >= 10.0
    cols = df.columns
    sql = ibis.to_sql(df)
    expr = f'''
        COPY (
          WITH t1 AS ({sql})
          SELECT json_group_array(struct_pack({cols}))
          AS cells
          FROM t1
        ) TO '{path}' (FORMAT JSON)
    '''
    con.raw_sql(expr)


def geom_to_cell (df, zoom = 3):
    con = df._find_backend() # df.get_backend() ibis >= 10.0
    sql = ibis.to_sql(df)
    expr = f'''
        WITH t1 AS (
        SELECT *, ST_Dump(geom) AS geom 
        FROM ({sql})
        ) 
        SELECT *,
           h3_polygon_wkt_to_cells_string(UNNEST(geom).geom, {zoom}) AS h{zoom}
        FROM t1
    '''

    con.sql(expr)



# .to_parquet(f"s3://public-biodiversity/pad-us-4/pad-h3-z{zoom}.parquet")

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
def h3_cell_to_parent(cell, zoom: int) -> int:
    ...


@ibis.udf.scalar.builtin
def h3_cell_to_parent_string(cell, zoom: int) -> str:
    ...