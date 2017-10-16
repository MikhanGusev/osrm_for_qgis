This is an experimental QGIS plugin for routing with OSRM.

Example: define start and end point and a route will be calculated (less than a second on a common laptop with 150K lines layer) and displayed in QGIS:

![Screenshot_1](/art/screen1_ru.png)

How does it work: currently the plugin just calls some external test OSRM utility (should be defined in plugin settings) with command line arguments (start and end point coordinates) and loads the resulting GeoJSON path into QGIS as a layer. All data which is required for OSRM routing mechanism must be created as usual with the help of osrm-extract and osrm-contract outside of QGIS. The purpose in future is to create a plugin with the similar functionality as in https://github.com/nextgis/gnm_qgis but based on the "OSRM engine".