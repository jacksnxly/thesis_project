import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from geopy.geocoders import Nominatim
from shapely.geometry import Point
import time

def geocode_locations(df):
    # Initialize geocoder with proper user agent
    geolocator = Nominatim(user_agent="startup_funding_analysis")
    
    # Try to load existing geocoded data
    try:
        geo_df = pd.read_csv('data/processed/geocoded_locations.csv')
        # Convert geometry string to Point objects
        from shapely import wkt
        geo_df['geometry'] = geo_df['geometry'].apply(wkt.loads)
        return gpd.GeoDataFrame(geo_df, geometry='geometry', crs="EPSG:4326")
    except FileNotFoundError:
        print("Geocoding locations...")

    locations = []
    for _, row in df.iterrows():
        location = None
        query = f"{row['Headquarters City']}, {row['Headquarters State']}, Germany"
        
        try:
            location = geolocator.geocode(query)
            if location:
                locations.append({
                    'City': row['Headquarters City'],
                    'State': row['Headquarters State'],
                    'Funding': row['Total Funding Amount (converted)'],
                    'geometry': Point(location.longitude, location.latitude)
                })
            time.sleep(1)  # Respect rate limits
        except Exception as e:
            print(f"Error geocoding {query}: {e}")
    
    geo_df = gpd.GeoDataFrame(locations, crs="EPSG:4326")
    geo_df.to_csv('data/processed/geocoded_locations.csv', index=False)
    return geo_df

def load_germany_base_map():
    # Get Germany border from Natural Earth direct download
    natural_earth_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    try:
        world = gpd.read_file(natural_earth_url)
        germany = world[world.NAME == "Germany"]
        if germany.empty:
            raise ValueError("Germany not found in Natural Earth dataset")
        return germany
    except Exception as e:
        print(f"Error loading base map: {e}")
        raise

def create_visualizations(geo_df, germany):
    # Static plot
    fig, ax = plt.subplots(figsize=(16, 10))
    germany.plot(ax=ax, color='lightgrey', edgecolor='black')
    # Convert funding to numeric and handle missing values
    geo_df['Funding'] = pd.to_numeric(geo_df['Funding'], errors='coerce').fillna(0)
    
    # Create size column with debug output
    print("Funding values sample:", geo_df['Funding'].head())
    geo_df['size'] = (geo_df['Funding'] / 50000).clip(lower=1).astype(float)
    print("Size values sample:", geo_df['size'].head())
    
    if geo_df.empty:
        raise ValueError("No geocoded data available for plotting")
        
    # Filter out zero funding entries
    valid_funding = geo_df[geo_df['Funding'] > 0]
    
    # Create scatter plot directly from GeoDataFrame
    scatter = ax.scatter(
        x=valid_funding.geometry.x,
        y=valid_funding.geometry.y,
        s=valid_funding['size']*10,
        c=valid_funding['Funding'],
        cmap='YlOrRd',
        alpha=0.6,
        edgecolor='k',
        linewidth=0.5
    )
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Funding Amount (€)')
    plt.title("Startup Funding Distribution in Germany")
    plt.savefig('data/processed/funding_heatmap.png', dpi=300, bbox_inches='tight')
    
    # Interactive map
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)
    folium.GeoJson(germany).add_to(m)
    
    for _, row in geo_df.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=max(float(row['Funding'])/500000, 1),  # Ensure numeric and minimum size
            color='#ff7800',
            fill=True,
            fill_color='#ff7800',
            popup=f"{row['City']}: €{row['Funding']:,.0f}"
        ).add_to(m)
    
    m.save('data/processed/funding_heatmap_interactive.html')

if __name__ == "__main__":
    # Load and process data
    df = pd.read_csv('data/processed/cleaned_funding_20250124003849.csv')
    geo_df = geocode_locations(df)
    germany = load_germany_base_map()
    
    # Create visualizations
    create_visualizations(geo_df, germany)
