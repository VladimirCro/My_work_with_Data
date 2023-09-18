import os
from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsFeature, QgsGeometry, QgsVectorFileWriter
from PyQt5.QtGui import QColor

# Define the path to the trackplot file
trackplot_file = 'RTE_UXO-DRASSM-23_CM2_Z3_SBP_Trackplot_LIN.shp'

# Load the trackplot layer
trackplot_layer = QgsVectorLayer(trackplot_file, 'Trackplot', 'ogr')
if not trackplot_layer.isValid():
    print(f'Error: Could not load trackplot layer from {trackplot_file}')
else:
    QgsProject.instance().addMapLayer(trackplot_layer)

    # Create a memory layer to store the polygons
    mem_layer = QgsVectorLayer('Polygon?crs=epsg:4326', 'Polygons', 'memory')
    prov = mem_layer.dataProvider()

    # Add fields to the memory layer
    fields = QgsFields()
    fields.append(QgsField('Area', QVariant.Double))
    fields.append(QgsField('Lines', QVariant.String))
    prov.addAttributes(fields)
    mem_layer.updateFields()

    # Create a list to store the polygons
    polygons = []

    # Iterate over each feature in the trackplot layer
    for feature in trackplot_layer.getFeatures():
        # Get the geometry of the feature
        geom = feature.geometry()

        # Initialize a list to store the points with distances > 50m
        points_above_50m = []

        # Iterate over each point in the line
        for point in geom.vertices():
            min_distance = float('inf')
            closest_line = None

            # Iterate over all other features to find the closest line
            for other_feature in trackplot_layer.getFeatures():
                if other_feature.id() != feature.id():
                    other_geom = other_feature.geometry()
                    dist = point.distance(other_geom)
                    if dist < min_distance:
                        min_distance = dist
                        closest_line = other_feature['Line']

            # If the minimum distance is greater than 50m, add the point to the list
            if min_distance > 50:
                points_above_50m.append(point)

        # Create a polygon from the points above 50m
        if len(points_above_50m) > 1:
            poly_geom = QgsGeometry.fromPolygonXY([points_above_50m])
            poly_feat = QgsFeature()
            poly_feat.setGeometry(poly_geom)
            poly_feat.setAttributes([poly_geom.area(), closest_line])
            polygons.append(poly_feat)

    # Add the polygons to the memory layer
    prov.addFeatures(polygons)

    # Save the memory layer as a shapefile
    output_path = '/Results/output.shp'
    QgsVectorFileWriter.writeAsVectorFormat(mem_layer, output_path, 'utf-8', mem_layer.crs(), 'ESRI Shapefile')

    # Load the output layer
    output_layer = QgsVectorLayer(output_path, 'Output', 'ogr')
    if not output_layer.isValid():
        print(f'Error: Could not load output layer from {output_path}')
    else:
        QgsProject.instance().addMapLayer(output_layer)

        # Set symbology for the output layer (black hatch lines)
        symbol = output_layer.renderer().symbol()
        if symbol:
            symbol.setColor(QColor(0, 0, 0))
            symbol.symbolLayer(0).setStrokeStyle(Qt.PenStyle(Qt.SolidLine))
            symbol.symbolLayer(0).setStrokeWidth(0.8)
            output_layer.triggerRepaint()

        # Print a message when the script is finished
        print('Script completed.')
