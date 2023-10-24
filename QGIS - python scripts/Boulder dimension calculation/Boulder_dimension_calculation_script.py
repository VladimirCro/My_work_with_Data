import os
import geopandas as gpd
import rasterio
import pandas as pd 
from shapely.geometry import Point

# Define input and output file paths
input_polygon_layer_path = 'Boulder polygons/BE3956H-511_B02_ManualyPickedBoulders.shp'
input_raster_path = 'MBES grid/BE3956H-511_B02_2020_10_ETRS89_UTM33N_DHHN92_MB_#0.15_Encoded.tif'
output_layer_path = 'Boulder polygons/target_list.shp'

# User-defined block name
block_name = 'B02'

# Read the input polygon layer (boulder polygons)
polygon_layer = gpd.read_file(input_polygon_layer_path)

# Open the bathymetric raster
with rasterio.open(input_raster_path) as src:
    target_list = []

    for index, row in polygon_layer.iterrows():
        # Calculate the centroid of each polygon
        centroid = row['geometry'].centroid

        # Get the coordinates (Easting, Northing)
        easting, northing = centroid.x, centroid.y

        # Get the depth at the centroid
        depth = next(src.sample([(easting, northing)]))[0]

        # Calculate Length and Width
        length = row['geometry'].length
        width = row['geometry'].area / length

        # Calculate Height (the difference in depth)
        height = abs(depth)

        # Generate a unique identifier (Target ID)
        target_id = f'MBES_{block_name}_{index}'

        # Create a dictionary with attribute data
        attributes = {
            'Poly_ID': index,  # You can use the index as Poly_ID or another unique identifier
            'Target_ID': target_id,
            'Block': block_name,
            'KP': '',
            'DCC': '',
            'Easting': easting,
            'Northing': northing,
            'WaterDepth': depth,
            'Length': length,
            'Width': width,
            'Height': height
        }

        target_list.append(attributes)

    # Create a GeoDataFrame for the target list and add attributes
    target_gdf = gpd.GeoDataFrame(target_list, geometry=gpd.points_from_xy([attr['Easting'] for attr in target_list], [attr['Northing'] for attr in target_list]))

    # Write the target list to the output file
    if not os.path.exists(output_layer_path):
        target_gdf.to_file(output_layer_path, driver='ESRI Shapefile')
    else:
        # Append to the existing file if it already exists
        existing_layer = gpd.read_file(output_layer_path)
        combined_gdf = pd.concat([existing_layer, target_gdf], ignore_index=True)
        combined_gdf.to_file(output_layer_path, driver='ESRI Shapefile')

# Print a message indicating successful completion
print('Task completed successfully.')


