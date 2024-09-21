# Specifications

+ The tool has to be hosted/deployed as a web app:
+ It will receive as input a shapefile with the area of interest (aoi) and the range of dates to perform the calculation.
+ It will calculate the soils loss based in the (Revised Universal Soil Loss Equation) RUSLE equation.
    + It will give the option to the user to load his own layers for the RUSLE as shapefiles.
    + If some layer is not provided, it will use the remote sensing proxies retrieved from Google Earth Engine (using python API).
+ The output will be visualized as a map showing the soil loss and alternativelly, it will display the intermediate layers for the calculation of it.

```mermaid
graph TD
    subgraph User Interface
        A[User] -->|Uploads Shapefile<br/>Selects Options| B[Web Application]
    end

    subgraph Backend [Backend (Django + GeoDjango)]
        B --> C[Process Input Shapefile]
        C --> D{All RUSLE Layers Provided?}
        D -- Yes --> E[Calculate RUSLE]
        D -- No --> F[Retrieve Missing Layers via GEE API]
        F --> E
        E --> G[Store Results in Database]
    end

    subgraph Database
        G --> H[PostGIS]
    end

    subgraph Frontend [Frontend]
        H --> I[Generate Map Visualizations]
        I --> J[Display Soil Loss Map<br/>and Intermediate Layers]
        J --> A
    end

```