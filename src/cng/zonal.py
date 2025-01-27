import subprocess

# reprojecting raster data 
def raster_reprojection(input_file, output_file, epsg="EPSG:3310"):
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
