import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import plotly.express as px
import logging
import time

# Configure logging
logging.basicConfig(filename='logs/geocoding.log', level=logging.INFO)

def main():
    # Load cleaned data
    df = pd.read_csv('data/processed/cleaned_funding_20250124003849.csv')
    
    # Aggregate startups per city
    city_counts = df.groupby(['Headquarters City', 'Headquarters State']).size().reset_index(name='Startup Count')
    
    # Initialize geocoder with cache and rate limiting
    geolocator = Nominatim(user_agent="startup_heatmap")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=2)
    
    # Geocode cities
    locations = []
    for idx, row in city_counts.iterrows():
        try:
            location = geocode(f"{row['Headquarters City']}, {row['Headquarters State']}, Germany")
            if location:
                locations.append({
                    'City': row['Headquarters City'],
                    'State': row['Headquarters State'],
                    'Startup Count': row['Startup Count'],
                    'Latitude': location.latitude,
                    'Longitude': location.longitude
                })
            else:
                logging.warning(f"Could not geocode: {row['Headquarters City']}, {row['Headquarters State']}")
        except Exception as e:
            logging.error(f"Error geocoding {row['Headquarters City']}: {str(e)}")
        time.sleep(1)  # Extra buffer for API limits
    
    # Create DataFrame from successful geocodes
    geo_df = pd.DataFrame(locations)
    
    # Create heatmap figure
    fig = px.density_mapbox(geo_df,
                            lat='Latitude',
                            lon='Longitude',
                            z='Startup Count',
                            radius=25,
                            center={"lat": 51.1657, "lon": 10.4515},  # Central Germany
                            zoom=4,
                            mapbox_style="open-street-map",
                            title='German Startup Distribution Heatmap')
    
    # Save static image
    fig.write_image("data/processed/startup_heatmap.png")
    fig.write_html("data/processed/startup_heatmap_interactive.html")

if __name__ == "__main__":
    main()
