from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsProject, QgsVectorFileWriter
from PyQt5.QtCore import QVariant

trackplot_file = r'C:\Users\vladi\Desktop\ZADATAK\HC-02-1-21-23_Hidrocibalae_Python programing task description\Distance between trackplots\RTE_UXO-DRASSM-23_CM2_Z3_SBP_Trackplot_LIN.shp'
output_polygon_file = r'C:\Users\vladi\Desktop\ZADATAK\HC-02-1-21-23_Hidrocibalae_Python programing task description\Distance between trackplots\output_polygon.shp'

trackplot_layer = QgsVectorLayer(trackplot_file, "Trackplot", "ogr")
if not trackplot_layer.isValid():
    print("Error: Trackplot layer not valid")
    exit()

output_layer = QgsVectorLayer("Polygon?crs=EPSG:32630", "Polygons", "memory")
output_layer_data = output_layer.dataProvider()
output_layer_data.addAttributes([
    QgsField("Area", QVariant.Double),
    QgsField("Line1", QVariant.String),
    QgsField("Line2", QVariant.String)
])
output_layer.updateFields()

polygon_geom = QgsGeometry()
polygons = []
features = [f for f in trackplot_layer.getFeatures()]

for i, feature1 in enumerate(features):
    line_name1 = feature1["Line"]
    geometry1 = feature1.geometry()
    neighboring_lines = []
    distances = []

    for j, feature2 in enumerate(features):
        if i == j:
            continue

        line_name2 = feature2["Line"]
        geometry2 = feature2.geometry()
        distance = geometry1.distance(geometry2)
        neighboring_lines.append(line_name2)
        distances.append(distance)

    if any(dist > 50 for dist in distances):
        polygon_geom = geometry1.difference(geometry1.intersection(geometry2))
        output_feature = QgsFeature()
        output_feature.setGeometry(polygon_geom)
        output_feature.setAttributes([
            polygon_geom.area(),
            line_name1,
            ", ".join(neighboring_lines)
        ])
        polygons.append(output_feature)

output_layer_data.addFeatures(polygons)
QgsVectorFileWriter.writeAsVectorFormat(
    output_layer,
    output_polygon_file,
    "utf-8",
    output_layer.crs(),
    "ESRI Shapefile"
)

QgsProject.instance().addMapLayer(output_layer)
