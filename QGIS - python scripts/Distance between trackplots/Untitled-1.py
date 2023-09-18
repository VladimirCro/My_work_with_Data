# Import required QGIS modules
from qgis.core import QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsFeature, QgsGeometry, QgsField

# Define the path to your trackplot shapefile
trackplot_path = '/path/to/trackplot.shp'

# Load the trackplot shapefile as a vector layer
trackplot_layer = QgsVectorLayer(trackplot_path, 'Trackplot', 'ogr')

# Check if the layer loaded successfully
if not trackplot_layer.isValid():
    print("Error: Unable to load trackplot layer")
else:
    # Create a new memory layer to store calculated polygons
    crs = trackplot_layer.crs()
    polygon_layer = QgsVectorLayer("Polygon?crs=" + crs.authid(), "Polygons", "memory")

    # Define the field names for the attribute table
    field_names = ["Area", "LineNames"]

    # Add the fields to the attribute table
    for field_name in field_names:
        polygon_layer.addAttribute(QgsField(field_name, QVariant.String))

    # Initialize a feature writer for the polygon layer
    polygon_writer = polygon_layer.dataProvider()

    # Get the distance threshold (50 meters)
    threshold_distance = 50

    # Iterate through each feature in the trackplot layer
    for trackplot_feature in trackplot_layer.getFeatures():
        trackplot_geometry = trackplot_feature.geometry()

        # Initialize a list to store polygon geometries and line names
        polygons = []
        line_names = []

        # Iterate through the vertices of the trackplot line
        for vertex in trackplot_geometry.vertices():
            # Create a buffer around each vertex
            buffer_geometry = vertex.buffer(threshold_distance, 8)

            # Iterate through the neighboring features (lines)
            for neighbor_feature in trackplot_layer.getFeatures():
                neighbor_geometry = neighbor_feature.geometry()

                # Check if the neighbor feature intersects with the buffer
                if buffer_geometry.intersects(neighbor_geometry):
                    # Calculate the intersection geometry
                    intersection = buffer_geometry.intersection(neighbor_geometry)

                    # Check if the intersection area is above the threshold
                    if intersection.area() > threshold_distance:
                        polygons.append(intersection)
                        line_names.append(neighbor_feature['Line'])

        # Create a single polygon geometry from the buffered intersections
        if polygons:
            combined_geometry = QgsGeometry.fromPolygonXY(polygons)

            # Create a new feature in the polygon layer
            polygon_feature = QgsFeature()
            polygon_feature.setGeometry(combined_geometry)
            polygon_feature.setAttributes([combined_geometry.area(), ', '.join(line_names)])

            # Add the feature to the polygon layer
            polygon_writer.addFeature(polygon_feature)

    # Save the polygon layer as a shapefile
    output_path = '/path/to/output_polygon.shp'
    QgsVectorFileWriter.writeAsVectorFormat(polygon_layer, output_path, 'utf-8', crs, 'ESRI Shapefile')

    # Add the polygon layer to the QGIS project
    QgsProject.instance().addMapLayer(polygon_layer)

    print(f"Script completed. Results saved to {output_path}")
