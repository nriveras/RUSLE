# Specifications

+ The tool has to be hosted/deployed as a web app:
+ It will receive as input a shapefile with the area of interest (aoi).
+ It will calculate the soils loss based in the (Revised Universal Soil Loss Equation) RUSLE equation.
    + It will give the option to the user to load his own layers for the RUSLE as shapefiles.
    + If some layer is not provided, it will use the remote sensing proxies retrieved from Google Earth Engine (using python API).
+ The output will be visualized as a map showing the soil loss and alternativelly, it will display the intermediate layers for the calculation of it.

```mermaid

The error you're encountering is due to Mermaid not interpreting the `|` character properly in the label text. To fix this, you should use the `-->` syntax without the `|` characters or split the conditions into separate arrows. Here’s a corrected version:

```mermaid
graph TD
    A[User] --> B[Web App (Flask or FastAPI)]
    B --> C{Are shapefiles provided?}
    C -->|Yes| D[Process with Geopandas and Fiona]
    C -->|No| E[Retrieve data from Google Earth Engine API]
    D --> F[Process RUSLE Layers]
    E --> F
    F --> G[Calculate Soil Loss]
    G --> H[Visualize Intermediate Layers (Bokeh/Plotly)]
    G --> I[Visualize Final Output (Leaflet/Folium)]
    H --> J[Display Intermediate Map]
    I --> K[Display Final Soil Loss Map]
    J --> L[Display Results to User]
    K --> L

    subgraph "GIS Processing"
    D
    E
    F
    end
    
    subgraph "Visualization"
    H
    I
    J
    K
    L
    end
    
    style B fill:#f9f,stroke:#333,stroke-width:2px;
    style "GIS Processing" fill:#bbf,stroke:#333,stroke-width:1px;
    style "Visualization" fill:#bfb,stroke:#333,stroke-width:1px;


```