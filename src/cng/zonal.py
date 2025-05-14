import subprocess

# reprojecting raster data 
def raster_reprojection_cli(input_file, output_file, epsg="EPSG:3310"):
    cmd = [
        "gdalwarp",
        "-t_srs", epsg,
        input_file,
        output_file
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Reprojection successful! Output saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during reprojection: {e}")


# alternate reprojection via gdal python package
from osgeo import gdal
def raster_reprojection(input_file, output_file, dst_srs):
    """
    Reprojects a raster file using the GDAL Python package.

    Args:
    input_file (str): The path to the input raster file.
    output_file (str): The path to the output reprojected raster file.
    dst_srs (str): The EPSG code of the desired coordinate reference system.

    Examples:
    gdal_warp("/vsicurl/https://data.source.coop/cboettig/mobi/species-richness-all/mobi-species-richness.tif", "mobi.xyz", 'EPSG:4326')

    Returns:
    None
    """

    ds = gdal.Open(input_file)
    src_srs = ds.GetProjection()
    warp_options = gdal.WarpOptions(dstSRS=dst_srs)
    gdal.Warp(output_file, ds, options=warp_options)

