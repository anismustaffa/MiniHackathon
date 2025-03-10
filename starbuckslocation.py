
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import folium

# 📌 Load datasets
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
icon_path = "./data/starbucks-icon.png"  # Ensure this is the correct path

# 📌 **Option 1: Static Map using Matplotlib & GeoPandas**
def plot_static_map():
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot neighborhoods
    neighborhoods.plot(ax=ax, color='lightgray', edgecolor='black', alpha=0.5)

    # Plot Starbucks locations as small red dots
    denver_gdf.plot(ax=ax, markersize=15, color='red', alpha=0.8, label="Starbucks Locations")

    # Function to add Starbucks icon at each location
    def add_icon(x, y, ax, icon_path, zoom=0.003):  # 🔥 Reduced size by 80% (from 0.015)
        icon = Image.open(icon_path)
        im = OffsetImage(icon, zoom=zoom)
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax.add_artist(ab)

    # Add icons at Starbucks locations
    for _, row in denver.iterrows():
        add_icon(row['Longitude'], row['Latitude'], ax, icon_path, zoom=0.003)  # Smaller size

    # ✅ Fix the legend by ensuring both the icon and text are added
    legend_icon = OffsetImage(Image.open(icon_path), zoom=0.006)  # Reduced zoom by 40%
    legend_ab = AnnotationBbox(legend_icon, (0.91, 0.05), frameon=False, xycoords="axes fraction")
    ax.add_artist(legend_ab)  # ✅ Ensure the Starbucks icon is added to the plot

    # ✅ Adjust text position so it aligns better with the icon
    ax.text(0.93, 0.05, "Starbucks Locations", transform=ax.transAxes, fontsize=6, verticalalignment='center', fontweight='bold')

    # Customize plot
    plt.title("Starbucks Locations in Denver", fontsize=15)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)

    # Save and display the static plot
    plt.savefig("denver_starbucks_static_map.png", dpi=300)
    plt.show(block=True)
    print("Static map saved as 'denver_starbucks_static_map2.png'.")
    
plot_static_map()   
    

