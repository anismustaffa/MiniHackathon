import pandas as pd
import geopandas as gpd
import folium

# ✅ Step 1: Load Census Data
file_path = "./data/census.csv"
census = pd.read_csv(file_path)

# ✅ Step 2: Check and Rename Columns If Needed
print("Census Data Columns:", census.columns.tolist())

# Convert NBHD_ID to the same type
census["NBHD_ID"] = census["NBHD_ID"].astype(str)

# Ensure relevant columns are numeric
census[['NUM_HHLD_100K+', 'NUM_HOUSEHOLDS', 'AGE_18_TO_34', 'POPULATION_2010']] = census[
    ['NUM_HHLD_100K+', 'NUM_HOUSEHOLDS', 'AGE_18_TO_34', 'POPULATION_2010']
].apply(pd.to_numeric, errors='coerce')

# Drop rows where household count or population is zero
census = census[(census['NUM_HOUSEHOLDS'] > 0) & (census['POPULATION_2010'] > 0)]

# Fill missing values in NUM_HHLD_100K+ with 0
census = census.copy()
census.loc[:, 'NUM_HHLD_100K+'] = census['NUM_HHLD_100K+'].fillna(0)

# ✅ Step 3: Compute Rankings
census['Affluent_Ratio'] = census['NUM_HHLD_100K+'] / census['NUM_HOUSEHOLDS']
census['Young_Adult_Ratio'] = census['AGE_18_TO_34'] / census['POPULATION_2010']
census['Score'] = (census['Affluent_Ratio'] + census['Young_Adult_Ratio']) / 2

# ✅ Step 4: Get Top 3 Neighborhoods
top_neighborhoods = census[['NBHD_ID', 'NBHD_NAME', 'Affluent_Ratio', 'Young_Adult_Ratio', 'Score']].sort_values(
    by='Score', ascending=False
).head(3)

print("🏆 **Top 3 Neighborhoods for the New Store** 🏆")
print(top_neighborhoods.to_string(index=False))

# ✅ Step 5: Load and Merge Neighborhood Shapefile
shapefile_path = "./data/neighborhoods.shp"

try:
    neighborhoods = gpd.read_file(shapefile_path)
    print("Neighborhoods Data Columns:", neighborhoods.columns.tolist())  
except Exception as e:
    print(f"Error loading shapefile: {e}")
    exit()
    

# Convert NBHD_ID in neighborhoods to the same type as census
neighborhoods["NBHD_ID"] = neighborhoods["NBHD_ID"].astype(str)

# ✅ Fix: Convert invalid geometries to valid format
neighborhoods["geometry"] = neighborhoods["geometry"].apply(lambda geom: geom if geom.is_valid else geom.buffer(0))

# Remove null geometries
neighborhoods = neighborhoods[neighborhoods["geometry"].notnull()]

# Merge Data
merged = neighborhoods.merge(top_neighborhoods, on='NBHD_ID', how='inner')

# ✅ Debugging Step: Print merged DataFrame columns
print("Merged DataFrame Columns:", merged.columns.tolist())
print("Merged DataFrame Preview:\n", merged.head())

# ✅ Step 6: Map the Top 3 Neighborhoods
color_mapping = {0: "red", 1: "blue", 2: "green"}

# Initialize map centered on Denver
map_center = [39.7392, -104.9903]
m = folium.Map(location=map_center, zoom_start=11)

for idx, row in merged.iterrows():
    color = color_mapping[idx] if idx in color_mapping else "gray"
    folium.GeoJson(
        row["geometry"],
        name=row["NBHD_NAME_x"],  # ✅ Use the correct column name
        style_function=lambda feature, color=color: {
            "fillColor": color,
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.6,
        },
        tooltip=row["NBHD_NAME_x"]  # ✅ Update tooltip with correct column
    ).add_to(m)

# ✅ Step 7: Save the Map
map_path = "top_3_neighborhoods_map.html"
m.save(map_path)

# ✅ Final Output
print(f"✅ Interactive map saved as '{map_path}'. Open this file in your browser.")
