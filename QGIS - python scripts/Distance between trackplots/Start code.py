import os
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsVectorFileWriter
from qgis.PyQt.QtGui import QColor

# Replace with your file paths
trackplot_file = '/path/to/trackplot.shp'
output_polygon_file = '/path/to/output_polygon.shp'

# Add the trackplot file to QGIS project
trackplot_layer = QgsVectorLayer(trackplot_file, 'Trackplots', 'ogr')
QgsProject.instance().addMapLayer(trackplot_layer)

# Create a memory layer for the output polygons
output_polygon_layer = QgsVectorLayer('Polygon?crs=epsg:4326', 'Output Polygons', 'memory')
output_polygon_layer.startEditing()

# Define fields for the attribute table
output_polygon_layer.addAttribute(QgsField('Area', QVariant.Double))
output_polygon_layer.addAttribute(QgsField('Lines', QVariant.String))

# Initialize the features
features = []

# Iterate over the trackplot features
for trackplot_feature in trackplot_layer.getFeatures():
    # Extract required information from the trackplot feature
    date = trackplot_feature['Date']
    line = trackplot_feature['Line']
    direction = trackplot_feature['Direction']
    geometry = trackplot_feature.geometry()
    
    # Calculate and create polygons where distance exceeds 50 meters
    points = geometry.asMultiPoint()
    polygons = []
    for i in range(len(points) - 1):
        distance = points[i].distance(points[i + 1])
        if distance > 50:
            polygon = QgsGeometry.fromPolygonXY([[points[i], points[i + 1], points[i + 1].project(direction, distance), points[i].project(direction, distance)]]).convexHull()
            polygons.append(polygon)
            
            # Create a new feature for each polygon
            output_feature = QgsFeature(output_polygon_layer.fields())
            output_feature.setGeometry(polygon)
            output_feature['Area'] = polygon.area()
            output_feature['Lines'] = f'{line}-{date}'
            features.append(output_feature)

# Add the features to the output polygon layer
output_polygon_layer.addFeatures(features)
output_polygon_layer.commitChanges()

# Save the output polygon layer to a shapefile
QgsVectorFileWriter.writeAsVectorFormat(output_polygon_layer, output_polygon_file, 'utf-8', QgsCoordinateReferenceSystem('EPSG:4326'), 'ESRI Shapefile')

# Add the output polygon layer to the QGIS project
output_polygon_layer = QgsVectorLayer(output_polygon_file, 'Output Polygons', 'ogr')
QgsProject.instance().addMapLayer(output_polygon_layer)

# Symbolize the output polygon layer with hatch lines and black color
output_polygon_layer.renderer().symbol().setColor(QColor(0, 0, 0))
output_polygon_layer.renderer().symbol().symbolLayer(0).setBrushStyle(45)

# Refresh the map canvas
iface.mapCanvas().refresh()
