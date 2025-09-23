import requests
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

def get_weather_data(city_name, latitude, longitude):
    """Get weather data for a specific city using Open-Meteo API"""
    print(f"🌤️ Fetching weather data for {city_name}...")
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "weather_code"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
        "timezone": "Asia/Ho_Chi_Minh",
        "forecast_days": 7
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Create hourly data DataFrame
        hourly_df = pd.DataFrame({
            "city": city_name,
            "datetime": data["hourly"]["time"],
            "temperature_c": data["hourly"]["temperature_2m"],
            "humidity_percent": data["hourly"]["relative_humidity_2m"],
            "wind_speed_kmh": data["hourly"]["wind_speed_10m"],
            "wind_direction_deg": data["hourly"]["wind_direction_10m"],
            "wind_gusts_kmh": data["hourly"]["wind_gusts_10m"],
            "weather_code": data["hourly"]["weather_code"]
        })
        
        # Calculate wind index (0-100 scale based on speed and gusts)
        # Wind index formula: combines wind speed and gusts with weighting
        hourly_df["wind_index"] = (
            (hourly_df["wind_speed_kmh"] * 0.7 + hourly_df["wind_gusts_kmh"] * 0.3) / 50 * 100
        ).round(1).clip(0, 100)
        
        # Add wind direction categories
        def get_wind_direction_name(degrees):
            if pd.isna(degrees):
                return "Unknown"
            directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                         "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
            idx = round(degrees / 22.5) % 16
            return directions[idx]
        
        hourly_df["wind_direction_name"] = hourly_df["wind_direction_deg"].apply(get_wind_direction_name)
        
        # Create daily data DataFrame
        daily_df = pd.DataFrame({
            "city": city_name,
            "date": data["daily"]["time"],
            "temp_max_c": data["daily"]["temperature_2m_max"],
            "temp_min_c": data["daily"]["temperature_2m_min"],
            "precipitation_mm": data["daily"]["precipitation_sum"],
            "wind_speed_max_kmh": data["daily"]["wind_speed_10m_max"],
            "wind_gusts_max_kmh": data["daily"]["wind_gusts_10m_max"],
            "wind_direction_dominant_deg": data["daily"]["wind_direction_10m_dominant"]
        })
        
        # Calculate daily wind index
        daily_df["wind_index_max"] = (
            (daily_df["wind_speed_max_kmh"] * 0.7 + daily_df["wind_gusts_max_kmh"] * 0.3) / 50 * 100
        ).round(1).clip(0, 100)
        
        # Add dominant wind direction names for daily data
        daily_df["wind_direction_dominant_name"] = daily_df["wind_direction_dominant_deg"].apply(get_wind_direction_name)
        
        print(f"✅ Successfully fetched data for {city_name}")
        return hourly_df, daily_df, data
        
    except Exception as e:
        print(f"❌ Error fetching data for {city_name}: {e}")
        return None, None, None

def create_temperature_charts(hourly_data, daily_data):
    """Create temperature charts using matplotlib"""
    print("\n📊 Creating temperature charts...")
    
    # Set up matplotlib style
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (15, 10)
    plt.rcParams['font.size'] = 10
    
    # Convert datetime strings to datetime objects
    hourly_data['datetime_parsed'] = pd.to_datetime(hourly_data['datetime'])
    daily_data['date_parsed'] = pd.to_datetime(daily_data['date'])
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('🇻🇳 Vietnam Weather Analysis - Temperature by Time', fontsize=16, fontweight='bold')
    
    # Define colors for each city
    city_colors = {
        'Hà Nội': '#FF6B6B',
        'Hồ Chí Minh': '#4ECDC4', 
        'Đà Nẵng': '#45B7D1',
        'Quy Nhơn': '#96CEB4'
    }
    
    # Chart 1: Hourly Temperature Trends
    ax1.set_title('Hourly Temperature Trends (7 Days)', fontweight='bold')
    for city in hourly_data['city'].unique():
        city_data = hourly_data[hourly_data['city'] == city]
        ax1.plot(city_data['datetime_parsed'], city_data['temperature_c'], 
                label=city, color=city_colors[city], linewidth=2, alpha=0.8)
    
    ax1.set_xlabel('Date & Time')
    ax1.set_ylabel('Temperature (°C)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Chart 2: Daily Temperature Range (Min/Max)
    ax2.set_title('Daily Temperature Range (Min/Max)', fontweight='bold')
    x_offset = 0
    bar_width = 0.2
    
    for i, city in enumerate(daily_data['city'].unique()):
        city_data = daily_data[daily_data['city'] == city]
        x_pos = range(len(city_data))
        x_pos_adjusted = [x + i * bar_width for x in x_pos]
        
        # Create bars for min and max temperatures
        bars_max = ax2.bar(x_pos_adjusted, city_data['temp_max_c'], bar_width, 
                          label=f'{city} Max', color=city_colors[city], alpha=0.8)
        bars_min = ax2.bar(x_pos_adjusted, city_data['temp_min_c'], bar_width, 
                          label=f'{city} Min', color=city_colors[city], alpha=0.4)
    
    ax2.set_xlabel('Days')
    ax2.set_ylabel('Temperature (°C)')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # Chart 3: Temperature vs Wind Speed Scatter
    ax3.set_title('Temperature vs Wind Speed', fontweight='bold')
    for city in hourly_data['city'].unique():
        city_data = hourly_data[hourly_data['city'] == city]
        ax3.scatter(city_data['temperature_c'], city_data['wind_speed_kmh'], 
                   label=city, color=city_colors[city], alpha=0.6, s=20)
    
    ax3.set_xlabel('Temperature (°C)')
    ax3.set_ylabel('Wind Speed (km/h)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Chart 4: Average Temperature by City
    ax4.set_title('Average Temperature by City', fontweight='bold')
    city_avg_temps = hourly_data.groupby('city')['temperature_c'].mean().sort_values(ascending=False)
    
    bars = ax4.bar(range(len(city_avg_temps)), city_avg_temps.values, 
                   color=[city_colors[city] for city in city_avg_temps.index])
    ax4.set_xticks(range(len(city_avg_temps)))
    ax4.set_xticklabels(city_avg_temps.index, rotation=45)
    ax4.set_ylabel('Average Temperature (°C)')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}°C', ha='center', va='bottom', fontweight='bold')
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Save the chart
    chart_filename = "vietnam_weather_data_charts.png"
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Temperature charts saved to: {chart_filename}")
    
    # Show the plot
    plt.show()
    
    return chart_filename

def main():
    """Main function to collect weather data for Vietnamese cities"""
    print("🇻🇳 Vietnam Weather Data Collection")
    print("=" * 50)
    
    # Vietnamese cities with their coordinates
    cities = {
        "Hà Nội": {"lat": 21.0285, "lon": 105.8542},
        "Hồ Chí Minh": {"lat": 10.8231, "lon": 106.6297},
        "Đà Nẵng": {"lat": 16.0471, "lon": 108.2068},
        "Quy Nhơn": {"lat": 13.7563, "lon": 109.2297}
    }
    
    all_hourly_data = []
    all_daily_data = []
    all_raw_data = {}
    
    # Collect data for each city
    for city_name, coords in cities.items():
        hourly_df, daily_df, raw_data = get_weather_data(
            city_name, coords["lat"], coords["lon"]
        )
        
        if hourly_df is not None and daily_df is not None:
            all_hourly_data.append(hourly_df)
            all_daily_data.append(daily_df)
            all_raw_data[city_name] = raw_data
    
    if all_hourly_data and all_daily_data:
        # Combine all data
        combined_hourly = pd.concat(all_hourly_data, ignore_index=True)
        combined_daily = pd.concat(all_daily_data, ignore_index=True)
        
        # Add collection timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        combined_hourly["collected_at"] = timestamp
        combined_daily["collected_at"] = timestamp
        
        # Save to CSV files (same name as Python file)
        base_filename = "vietnam_weather_data"
        
        # Save hourly data
        hourly_csv = f"{base_filename}_hourly.csv"
        combined_hourly.to_csv(hourly_csv, index=False, encoding="utf-8")
        print(f"📊 Saved hourly data to: {hourly_csv}")
        
        # Save daily data
        daily_csv = f"{base_filename}_daily.csv"
        combined_daily.to_csv(daily_csv, index=False, encoding="utf-8")
        print(f"📊 Saved daily data to: {daily_csv}")
        
        # Save raw JSON data
        json_file = f"{base_filename}_raw.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(all_raw_data, f, ensure_ascii=False, indent=2)
        print(f"📊 Saved raw data to: {json_file}")
        
        # Display summary
        print("\n📈 Data Summary:")
        print(f"   🏙️ Cities: {len(cities)}")
        print(f"   ⏰ Hourly records: {len(combined_hourly)}")
        print(f"   📅 Daily records: {len(combined_daily)}")
        print(f"   🕐 Collection time: {timestamp}")
        
        # Display sample data
        print("\n🌡️ Sample Hourly Data:")
        print(combined_hourly[["city", "datetime", "temperature_c", "wind_speed_kmh", "wind_index", "wind_direction_name"]].head(8))
        
        print("\n📅 Daily Summary by City:")
        daily_summary = combined_daily.groupby("city").agg({
            "temp_max_c": "mean",
            "temp_min_c": "mean",
            "precipitation_mm": "sum",
            "wind_speed_max_kmh": "mean",
            "wind_index_max": "mean"
        }).round(2)
        print(daily_summary)
        
        print("\n💨 Wind Analysis:")
        wind_analysis = combined_hourly.groupby("city").agg({
            "wind_speed_kmh": ["mean", "max"],
            "wind_index": ["mean", "max"],
            "wind_direction_name": lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown"
        }).round(2)
        wind_analysis.columns = ["avg_wind_speed", "max_wind_speed", "avg_wind_index", "max_wind_index", "dominant_direction"]
        print(wind_analysis)
        
        # Create temperature charts
        chart_filename = create_temperature_charts(combined_hourly, combined_daily)
        
        return combined_hourly, combined_daily, chart_filename
    
    else:
        print("❌ Failed to collect weather data")
        return None, None, None

if __name__ == "__main__":
    result = main()
    
    if result[0] is not None and result[1] is not None:
        hourly_data, daily_data, chart_filename = result
        print(f"\n🎉 Weather data collection and visualization completed successfully!")
        print(f"📁 Files saved in current directory with base name 'vietnam_weather_data'")
        print(f"📊 Temperature charts saved as: {chart_filename}")
    else:
        print("\n😞 Weather data collection failed. Please check the error messages above.")
