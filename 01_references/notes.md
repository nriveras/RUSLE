Introducción Google Earth Engine
# [4 de 21](https://youtu.be/P4qYo3OO6Sk?si=sCziRN4EUf1e6ztb)

## Visualize python version from QGIS terminal
```
import sys
sys.version
```
## Install new packages in the QGIS environment:

In the terminal:

```
/Applications/QGIS.app/Contents/MacOS/bin/pip3 install shapely
```

```
/Applications/QGIS.app/Contents/MacOS/bin/pip3 install --upgrade pip
```
source: https://gis.stackexchange.com/questions/351280/installing-python-modules-for-qgis-3-on-mac



# https://youtu.be/3zGcRAAoWgA?si=QX3jdztmOq37LOmX

In the pluggins menu of QGIS, install Google Earth Engine.
gee can be used through the Python console of QGIS.

# [6 de 21](https://youtu.be/md97MUuTWTs?si=cy4FjhnHnq42R8qa)

# [7 de 21](https://youtu.be/b0BLYbEA_Yk?si=ePjKXWZBHLuLqn14)

/Applications/QGIS.app/Contents/MacOS/bin/pip3 install earthengine-api

/Applications/QGIS.app/Contents/MacOS/bin/pip3 install --upgrade oauth2client


/Applications/QGIS.app/Contents/MacOS/bin/pip3 install gcloud

install from web installer 

https://cloud.google.com/sdk/docs/install
./google-cloud-sdk/bin/gcloud init

restart the computer

/Applications/QGIS.app/Contents/MacOS/bin/earthengine authenticate

ee_object.getInfo() # print the information of an ee_object

# [8 de 21](https://youtu.be/46THbSmrNlE?si=ig5gBRGE1zW8fJ5U)

/Applications/QGIS.app/Contents/MacOS/bin/pip3 install geemap

import geemap
from ee_plugin import Map
import ee

/Applications/QGIS.app/Contents/MacOS/bin/pip3 install --upgrade geemap earthengine-api

/Applications/QGIS.app/Contents/Resources/python

in case of problems, reinstall plugin


# [9 de 21](https://youtu.be/97Oo_6sej2E?si=V7f6pcmCG2qnadAn)

QGIs includes OpenStreetMap by default (Browser/XYZ Tiles/OpenStreetMap).
We can add others with Python:
 load the script 01_QGIS_BaseMaps.py

```{python}
# Mapa Base en QGIS

from qgis.PyQt.QtCore import QSettings
from qgis.utils import iface

# Fuentes
sources = []
sources.append(["connections-xyz","Google Maps","","","","https://mt1.google.com/vt/lyrs=m&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D","","19","0"])
sources.append(["connections-xyz","Google Satellite", "", "", "", "https://mt1.google.com/vt/lyrs=s&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D", "", "19", "0"])
sources.append(["connections-xyz","Google Terrain", "", "", "", "https://mt1.google.com/vt/lyrs=t&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D", "", "19", "0"])
sources.append(["connections-xyz","Google Terrain Hybrid", "", "", "", "https://mt1.google.com/vt/lyrs=p&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D", "", "19", "0"])
sources.append(["connections-xyz","Google Satellite Hybrid", "", "", "", "https://mt1.google.com/vt/lyrs=y&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D", "", "19", "0"])
sources.append(["connections-xyz","Stamen Terrain", "", "", "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL", "http://tile.stamen.com/terrain/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "20", "0"])
sources.append(["connections-xyz","Stamen Toner", "", "", "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL", "http://tile.stamen.com/toner/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "20", "0"])
sources.append(["connections-xyz","Stamen Toner Light", "", "", "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL", "http://tile.stamen.com/toner-lite/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "20", "0"])
sources.append(["connections-xyz","Stamen Watercolor", "", "", "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL", "http://tile.stamen.com/watercolor/%7Bz%7D/%7Bx%7D/%7By%7D.jpg", "", "18", "0"])
sources.append(["connections-xyz","Wikimedia Map", "", "", "OpenStreetMap contributors, under ODbL", "https://maps.wikimedia.org/osm-intl/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "20", "1"])
sources.append(["connections-xyz","Wikimedia Hike Bike Map", "", "", "OpenStreetMap contributors, under ODbL", "http://tiles.wmflabs.org/hikebike/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "17", "1"])
sources.append(["connections-xyz","Esri Boundaries Places", "", "", "", "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "20", "0"])
sources.append(["connections-xyz","Esri Gray (dark)", "", "", "", "http://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "16", "0"])
sources.append(["connections-xyz","Esri Gray (light)", "", "", "", "http://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "16", "0"])
sources.append(["connections-xyz","Esri National Geographic", "", "", "", "http://services.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "12", "0"])
sources.append(["connections-xyz","Esri Ocean", "", "", "", "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "10", "0"])
sources.append(["connections-xyz","Esri Satellite", "", "", "", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "17", "0"])
sources.append(["connections-xyz","Esri Standard", "", "", "", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "17", "0"])
sources.append(["connections-xyz","Esri Terrain", "", "", "", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "20", "0"])
sources.append(["connections-xyz","Esri Transportation", "", "", "", "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "20", "0"])
sources.append(["connections-xyz","Esri Topo World", "", "", "", "http://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D", "", "20", "0"])
sources.append(["connections-xyz","OpenStreetMap Standard", "", "", "OpenStreetMap contributors, CC-BY-SA", "http://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "19", "0"])
sources.append(["connections-xyz","OpenStreetMap H.O.T.", "", "", "OpenStreetMap contributors, CC-BY-SA", "http://tile.openstreetmap.fr/hot/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "19", "0"])
sources.append(["connections-xyz","OpenStreetMap Monochrome", "", "", "OpenStreetMap contributors, CC-BY-SA", "http://tiles.wmflabs.org/bw-mapnik/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "19", "0"])
sources.append(["connections-xyz","Strava All", "", "", "OpenStreetMap contributors, CC-BY-SA", "https://heatmap-external-b.strava.com/tiles/all/bluered/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "15", "0"])
sources.append(["connections-xyz","Strava Run", "", "", "OpenStreetMap contributors, CC-BY-SA", "https://heatmap-external-b.strava.com/tiles/run/bluered/%7Bz%7D/%7Bx%7D/%7By%7D.png?v=19", "", "15", "0"])
sources.append(["connections-xyz","Open Weather Map Temperature", "", "", "Map tiles by OpenWeatherMap, under CC BY-SA 4.0", "http://tile.openweathermap.org/map/temp_new/%7Bz%7D/%7Bx%7D/%7By%7D.png?APPID=1c3e4ef8e25596946ee1f3846b53218a", "", "19", "0"])
sources.append(["connections-xyz","Open Weather Map Clouds", "", "", "Map tiles by OpenWeatherMap, under CC BY-SA 4.0", "http://tile.openweathermap.org/map/clouds_new/%7Bz%7D/%7Bx%7D/%7By%7D.png?APPID=ef3c5137f6c31db50c4c6f1ce4e7e9dd", "", "19", "0"])
sources.append(["connections-xyz","Open Weather Map Wind Speed", "", "", "Map tiles by OpenWeatherMap, under CC BY-SA 4.0", "http://tile.openweathermap.org/map/wind_new/%7Bz%7D/%7Bx%7D/%7By%7D.png?APPID=f9d0069aa69438d52276ae25c1ee9893", "", "19", "0"])
sources.append(["connections-xyz","CartoDb Dark Matter", "", "", "Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.", "http://basemaps.cartocdn.com/dark_all/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "20", "0"])
sources.append(["connections-xyz","CartoDb Positron", "", "", "Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.", "http://basemaps.cartocdn.com/light_all/%7Bz%7D/%7Bx%7D/%7By%7D.png", "", "20", "0"])
sources.append(["connections-xyz","Bing VirtualEarth", "", "", "", "http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1", "", "19", "1"])


# Add sources to browser
for source in sources:
   connectionType = source[0]
   connectionName = source[1]
   QSettings().setValue("qgis/%s/%s/authcfg" % (connectionType, connectionName), source[2])
   QSettings().setValue("qgis/%s/%s/password" % (connectionType, connectionName), source[3])
   QSettings().setValue("qgis/%s/%s/referer" % (connectionType, connectionName), source[4])
   QSettings().setValue("qgis/%s/%s/url" % (connectionType, connectionName), source[5])
   QSettings().setValue("qgis/%s/%s/username" % (connectionType, connectionName), source[6])
   QSettings().setValue("qgis/%s/%s/zmax" % (connectionType, connectionName), source[7])
   QSettings().setValue("qgis/%s/%s/zmin" % (connectionType, connectionName), source[8])

# Update GUI
iface.reloadConnections()
```

If the interface does not update, restart QGIS.
In case a basemap cannot be visualize at certain altitude, change Basemap/<right click>/ edit connection.../max zoom level to 20 or other value 

# [10 de 21](https://youtu.be/wLrD9PEnAuw?si=ed2LsMURGQJjZFP8)

/Applications/QGIS.app/Contents/MacOS/bin/earthengine command -h

Check permissions, it only work with the university credentials

```{python}
# google earth engine in QGIS

import ee
from ee_plugin import Map

# add GEE text
v1 = ee.String("Geomatics GEE - QGIS")

print(v1)
print(type(v1))
print(v1.getInfo())

# imagen
image = ee.Image("LANDSAT/LT05/C01/T1/LT05_003069_20060516")

# legend in RGB
viz = {
    "bands": ["B5", "B4", "B3"],
    "min": 1,
    "max": 120,
    "gamma": 0.9
}

viz2 = {
    "bands": ["B3", "B2", "B1"],
    "min": 1,
    "max": 120,
    "gamma": 0.9
}
# plot
geometry = image.geometry()

Map.centerObject(geometry, 9)
Map.addLayer(image, viz, "L5_B543")
Map.addLayer(image, viz2, "L5_B321")
```

# [11 de 21](https://youtu.be/bJdmvZLYDG8?si=QJzL-jYNfzbn0ZGl)
Intro and installation to anaconda

# [12 de 21](https://youtu.be/6fpCL4mKoTo?si=Uz54hb1T0bPlUdY4)
environment setting in conda (i am not sure how this work in QGIS)

conda env list

# [13 de 21](https://youtu.be/VF7qk0kGfvI?si=2pYosjHkEml7tBCn)
Install jupyter notebook in separated environment and intro to it.

# [14 de 21](https://youtu.be/UzES72N-2go?si=b0cz9fRYGrlB-DKW)
install jupyterlab in separated environment and intro to it. It is an IDE optimized for notebooks.

# [15 de 21](https://youtu.be/nFIkK_IA-3Q?si=FZSyV5Z1XifujaYl)
Install ee in the separated envirotment, authentification, etc.

To execute python code from bash (or terminal??):
python -c "import ee;ee.initialize()" # the ; indicate the next order

# [16 de 21](https://youtu.be/aM8bghtr62c?si=A2_A2gbe-4kUjodv)
pip install geemap

# [17 de 21](https://youtu.be/fwFiIWx29vk?si=J8aD16kHhp44bIUm)
Same previous example of QGIS, but in jupyterlab

# [18 de 21](https://youtu.be/ueNQlp366IA?si=dvB1jyNCADuCdIdc)
R setup

# [19 de 21](https://youtu.be/bbplnd1qfEo?si=BIj8UilCdD43GESq)
Reticulate setup for Python in R

# [20 de 21](https://youtu.be/DCqfBYeiCNs?si=JuRUVOUbeoBzjINT)
RGEE setup and use

# [21 de 21](https://youtu.be/27AqQ1pxSZI?si=1hMHPwmAC4EUzxT-)
GEE setup in R 
