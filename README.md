# MiniHackathon
**Project**: Identifying Optimal Neighborhoods for a New Coffee Shop in Denver
## Overview
This project aims to identify the best neighborhoods in Denver, Colorado, for opening a new coffee shop. The client's target demographic includes affluent households and young adults aged 20-35. Using geographical and demographic data, we analyzed Denver's neighborhoods to determine the top areas that align with the client's requirements. This README provides an overview of the project, methodology, findings, and instructions for reproducing the analysis.
Data Sources
The analysis was conducted using the following datasets:

1. **Starbucks Locations in Denver**: Includes store numbers, names, addresses, and geographical coordinates.

2. **Neighborhood Geographical Information**: Contains neighborhood IDs, names, and polygon geometries.

3. **Demographic Information**: Provides population, age distribution, household counts, and income data for each neighborhood.

All data was sourced from publicly available repositories, including:

* Starbucks store locator (scraped by Chris Meller).
* City of Denver Open Data Catalog (CC BY 3.0 license).
* United States Census Bureau (publicly available information).

## Methodology
The analysis was conducted in two main steps:

1. **Visualization of Starbucks Locations**:
- Plotted Starbucks locations on a map of Denver to provide context.
- Created a static map using Matplotlib and GeoPandas.

2. **Identification of Top Neighborhoods**:

- Calculated the proportion of affluent households and young adults in each neighborhood.
- Ranked neighborhoods based on a composite score combining these proportions.
- Created an interactive map highlighting the top 3 neighborhoods.

## Code Implementation
### 1. **Visualizing Starbucks Locations**
The script starbuckslocation.py loads the Starbucks locations and neighborhood data, then creates a static map with Starbucks icons overlaid on Denver neighborhoods.

```ruby
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Load datasets
denver = pd.read_csv('./data/denver.csv')  # Starbucks locations
neighborhoods = gpd.read_file('./data/neighborhoods.shp')  # Denver neighborhoods

# Convert Longitude and Latitude to numeric values
denver['Longitude'] = pd.to_numeric(denver['Longitude'], errors='coerce')
denver['Latitude'] = pd.to_numeric(denver['Latitude'], errors='coerce')

# Drop rows with missing coordinates
denver = denver.dropna(subset=['Longitude', 'Latitude'])

# Convert Starbucks locations to GeoDataFrame
denver_gdf = gpd.GeoDataFrame(
    denver, geometry=gpd.points_from_xy(denver['Longitude'], denver['Latitude']), crs="EPSG:4326"
)

# Starbucks icon path
icon_path = "./data/starbucks-icon.png"

# Plot static map
def plot_static_map():
    fig, ax = plt.subplots(figsize=(10, 10))
    neighborhoods.plot(ax=ax, color='lightgray', edgecolor='black', alpha=0.5)
    denver_gdf.plot(ax=ax, markersize=15, color='red', alpha=0.8, label="Starbucks Locations")

    # Add Starbucks icons
    def add_icon(x, y, ax, icon_path, zoom=0.003):
        icon = Image.open(icon_path)
        im = OffsetImage(icon, zoom=zoom)
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax.add_artist(ab)

    for _, row in denver.iterrows():
        add_icon(row['Longitude'], row['Latitude'], ax, icon_path, zoom=0.003)

    # Add legend
    legend_icon = OffsetImage(Image.open(icon_path), zoom=0.006)
    legend_ab = AnnotationBbox(legend_icon, (0.91, 0.05), frameon=False, xycoords="axes fraction")
    ax.add_artist(legend_ab)
    ax.text(0.93, 0.05, "Starbucks Locations", transform=ax.transAxes, fontsize=6, verticalalignment='center', fontweight='bold')

    # Customize plot
    plt.title("Starbucks Locations in Denver", fontsize=15)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)

    # Save and display the static plot
    plt.savefig("denver_starbucks_static_map.png", dpi=300)
    plt.show(block=True)
    print("Static map saved as 'denver_starbucks_static_map.png'.")

plot_static_map()
```
### 2. **Identifying Top Neighborhoods**
The script top3neighborhood.py calculates the top neighborhoods based on demographic criteria and creates an interactive map.
```ruby
import pandas as pd
import geopandas as gpd
import folium

# Load Census Data
census = pd.read_csv("./data/census.csv")

# Clean and prepare data
census["NBHD_ID"] = census["NBHD_ID"].astype(str)
census[['NUM_HHLD_100K+', 'NUM_HOUSEHOLDS', 'AGE_18_TO_34', 'POPULATION_2010']] = census[
    ['NUM_HHLD_100K+', 'NUM_HOUSEHOLDS', 'AGE_18_TO_34', 'POPULATION_2010']
].apply(pd.to_numeric, errors='coerce')
census = census[(census['NUM_HOUSEHOLDS'] > 0) & (census['POPULATION_2010'] > 0)]
census['NUM_HHLD_100K+'] = census['NUM_HHLD_100K+'].fillna(0)

# Calculate scores
census['Affluent_Ratio'] = census['NUM_HHLD_100K+'] / census['NUM_HOUSEHOLDS']
census['Young_Adult_Ratio'] = census['AGE_18_TO_34'] / census['POPULATION_2010']
census['Score'] = (census['Affluent_Ratio'] + census['Young_Adult_Ratio']) / 2

# Get top 3 neighborhoods
top_neighborhoods = census[['NBHD_ID', 'NBHD_NAME', 'Affluent_Ratio', 'Young_Adult_Ratio', 'Score']].sort_values(
    by='Score', ascending=False
).head(3)

# Load neighborhood shapefile
neighborhoods = gpd.read_file("./data/neighborhoods.shp")
neighborhoods["NBHD_ID"] = neighborhoods["NBHD_ID"].astype(str)
neighborhoods["geometry"] = neighborhoods["geometry"].apply(lambda geom: geom if geom.is_valid else geom.buffer(0))
neighborhoods = neighborhoods[neighborhoods["geometry"].notnull()]

# Merge data
merged = neighborhoods.merge(top_neighborhoods, on='NBHD_ID', how='inner')

# Create interactive map
color_mapping = {0: "red", 1: "blue", 2: "green"}
map_center = [39.7392, -104.9903]
m = folium.Map(location=map_center, zoom_start=11)

for idx, row in merged.iterrows():
    color = color_mapping[idx] if idx in color_mapping else "gray"
    folium.GeoJson(
        row["geometry"],
        name=row["NBHD_NAME_x"],
        style_function=lambda feature, color=color: {
            "fillColor": color,
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.6,
        },
        tooltip=row["NBHD_NAME_x"]
    ).add_to(m)

# Save map
map_path = "top_3_neighborhoods_map.html"
m.save(map_path)
print(f"Interactive map saved as '{map_path}'.")
```

## Findings
1. **Visualization of Starbucks Locations in Denver**
   
The static map below shows the distribution of Starbucks stores across Denver. This visualization helps contextualize the coffee shop landscape and ensures the new store is not in direct competition with Starbucks.

![denver_starbucks_static_map](https://github.com/user-attachments/assets/d7efeca6-3c39-4f7f-af5d-c39203133368)

2. **Top 3 Recommended Neighborhoods**
   
Based on the analysis, the top 3 neighborhoods for opening a new coffee shop are:

- **Auraria**

- **University**

- **Central Park**

These neighborhoods have the highest proportions of affluent households and young adults, making them ideal for the client's target demographic.

![Screenshot 2025-03-09 205853](https://github.com/user-attachments/assets/0a87f341-73e0-48b8-b9f5-876af4c41b28)


## Interactive Map of Top 3 Neighborhoods
The interactive map below highlights the top 3 neighborhoods (Auraria, University, and Central Park) where the client should focus their search. Hover over the map to see neighborhood labels and details.

**Top 3 Neighborhoods Map**

[Click here for the interactive map](https://anismustaffa.github.io/MiniHackathon/folder1/top_3_neighborhoods_map.html)


## How to Reproduce the Analysis
**Clone the Repository:**
```ruby
git clone https://github.com/your-repo/coffee-shop-analysis.git
cd coffee-shop-analysis
```
**Install Dependencies:**

```ruby
pip install pandas geopandas folium matplotlib pillow
```
**Download the Data:**
Place all the files in the ./data/ directory:

* denver.csv
* neighborhoods.shp
* neighborhoods.dbf
* neighborhoods.shx
* census.csv
* starbucks-icon.png

**Run the Scripts:**

To visualize Starbucks locations:

```ruby
python starbuckslocation.py
To identify top neighborhoods and create the interactive map:
```
```ruby
python top3neighborhood.py
```
**View the Results:**

The static map will be saved as denver_starbucks_static_map.png.

The interactive map will be saved as top_3_neighborhoods_map.html.

## Conclusion
The analysis identified Auraria, University, and Central Park as the top neighborhoods for opening a new coffee shop in Denver. These areas have a high concentration of affluent households and young adults, aligning with the client's target demographic. The interactive map provides a clear visual representation of the recommended locations.
