# Lab02 - Collect Web Data

A comprehensive Python project for collecting and analyzing various types of web data including news articles, weather information, and cryptocurrency prices.

## 📋 Project Overview

This project demonstrates web scraping, API integration, data analysis, and visualization techniques. It consists of multiple components organized in different directories:

- **News Scraping**: Collect and summarize articles from VnExpress
- **Weather Data**: Multi-city weather tracking for Vietnamese cities
- **Cryptocurrency Tracking**: Real-time price monitoring with threshold alerts

## 🗂️ Project Structure

```
Lab02_Collect_Web_Data/
├── README.md                           # This file
├── lab02.ipynb                         # Original Jupyter notebook
├── baiviet.txt                         # Sample news articles output
├── weather.csv                         # Sample weather data
├── weather.json                        # Sample weather data (JSON)
├── bitcoin_price.txt                   # Sample Bitcoin price log
├── lab02_env/                          # Python virtual environment
├── extended-hw-part1/                  # News scraping enhancement
│   ├── enhanced_scraper.py             # Basic news scraper
│   ├── enhanced_scraper_v2.py          # Multi-category news scraper
│   └── *.csv                           # Generated news data files
├── extended-hw-part2/                  # Weather data collection
│   ├── vietnam_weather_data.py         # Multi-city weather tracker
│   ├── vietnam_weather_data_*.csv      # Weather data files
│   ├── vietnam_weather_data_charts.png # Temperature visualization
│   └── vietnam_weather_data_raw.json   # Raw weather API data
└── extended-hw-part3/                  # Cryptocurrency tracking
    ├── bitcoin_price_tracker.py        # Single Bitcoin tracker
    ├── multi_crypto_tracker.py         # Multi-crypto tracker with alerts
    ├── *.csv                           # Crypto price data files
    └── *.json                          # Raw crypto API data
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   cd /path/to/Lab02_Collect_Web_Data
   ```

2. **Create and activate virtual environment** (recommended)
   ```bash
   python3 -m venv lab02_env
   source lab02_env/bin/activate  # On Linux/Mac
   # or
   lab02_env\Scripts\activate     # On Windows
   ```

3. **Install required packages**
   ```bash
   pip install requests beautifulsoup4 pandas matplotlib
   ```

## 📊 Components Guide

### 1. News Scraping (extended-hw-part1)

Scrapes news articles from VnExpress with summarization and multi-page support.

**Files:**
- `enhanced_scraper.py` - Basic scraper with pagination
- `enhanced_scraper_v2.py` - Advanced scraper with category-based collection

**Usage:**
```bash
cd extended-hw-part1
python3 enhanced_scraper_v2.py
```

**Output:**
- `vnexpress_articles_categories_5pages.csv` - Article data with summaries
- Multiple categories: Trang chủ, Thời sự, Kinh doanh, Thể thao, Giải trí

**Features:**
- ✅ Article title extraction
- ✅ Full article links
- ✅ Content summarization
- ✅ Multi-category scraping
- ✅ CSV export with metadata

### 2. Weather Data Collection (extended-hw-part2)

Collects comprehensive weather data for major Vietnamese cities with visualization.

**File:** `vietnam_weather_data.py`

**Usage:**
```bash
cd extended-hw-part2
python3 vietnam_weather_data.py
```

**Cities Tracked:**
- 🏙️ Hà Nội (21.0285°N, 105.8542°E)
- 🏙️ Hồ Chí Minh (10.8231°N, 106.6297°E)
- 🏙️ Đà Nẵng (16.0471°N, 108.2068°E)
- 🏙️ Quy Nhơn (13.7563°N, 109.2297°E)

**Output Files:**
- `vietnam_weather_data_hourly.csv` - Hourly weather data
- `vietnam_weather_data_daily.csv` - Daily weather summaries
- `vietnam_weather_data_charts.png` - Temperature visualization charts
- `vietnam_weather_data_raw.json` - Complete API responses

**Features:**
- 🌡️ Temperature tracking
- 💨 Wind speed, direction, and custom wind index
- 💧 Humidity and precipitation data
- 📊 4-panel temperature visualization
- 📈 Statistical analysis and comparisons

### 3. Cryptocurrency Tracking (extended-hw-part3)

Real-time cryptocurrency price monitoring with threshold-based alerts.

**Files:**
- `bitcoin_price_tracker.py` - Single Bitcoin tracker
- `multi_crypto_tracker.py` - Multi-cryptocurrency tracker with alerts

**Usage:**
```bash
cd extended-hw-part3

# Single Bitcoin tracking
python3 bitcoin_price_tracker.py

# Multi-crypto tracking with alerts
python3 multi_crypto_tracker.py
```

**Cryptocurrencies Tracked:**
- ₿ **BTC** (Bitcoin)
- Ξ **ETH** (Ethereum)
- 🐕 **DOGE** (Dogecoin)

**Output Files:**
- `multi_crypto_tracker.csv` - Clean price data (time, symbol, usd_price)
- `multi_crypto_tracker_alerts.csv` - Threshold alert log
- `multi_crypto_tracker_detailed.csv` - Data with metadata
- `multi_crypto_tracker_raw.json` - Complete API responses

**Alert System:**
- 🚨 **HIGH ALERT**: Price above upper threshold
- ⚠️ **LOW ALERT**: Price below lower threshold
- ✅ **NORMAL**: Price within safe range

**Default Thresholds:**
- BTC: $110,000 - $113,000
- ETH: $4,000 - $4,100
- DOGE: $0.20 - $0.23

## 🔧 Configuration

### Weather Data Customization

Edit `vietnam_weather_data.py`:
```python
# Modify cities dictionary to add/change locations
cities = {
    "Your City": {"lat": latitude, "lon": longitude},
    # Add more cities...
}
```

### Crypto Alert Thresholds

Edit `multi_crypto_tracker.py`:
```python
# Modify PRICE_THRESHOLDS dictionary
PRICE_THRESHOLDS = {
    "BTC": {"high": 120000, "low": 100000},
    "ETH": {"high": 5000, "low": 3000},
    # Adjust thresholds as needed...
}
```

## 📈 Data Analysis Examples

### Weather Analysis
```python
import pandas as pd

# Load weather data
df = pd.read_csv('extended-hw-part2/vietnam_weather_data_hourly.csv')

# Analyze temperature by city
city_temps = df.groupby('city')['temperature_c'].agg(['mean', 'min', 'max'])
print(city_temps)
```

### Crypto Price Analysis
```python
import pandas as pd

# Load crypto data
df = pd.read_csv('extended-hw-part3/multi_crypto_tracker.csv')

# Analyze price changes
for symbol in df['symbol'].unique():
    symbol_data = df[df['symbol'] == symbol].sort_values('time')
    price_change = symbol_data['usd_price'].iloc[-1] - symbol_data['usd_price'].iloc[0]
    print(f"{symbol}: ${price_change:+.2f}")
```

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install requests beautifulsoup4 pandas matplotlib
   ```

2. **API Rate Limits**
   - The scripts include delays between requests
   - Reduce sample frequency if needed

3. **Network Issues**
   - Check internet connection
   - Some APIs may be temporarily unavailable

4. **Permission Errors**
   - Ensure write permissions in project directory
   - Run with appropriate user permissions

### Virtual Environment Issues

If you encounter package conflicts:
```bash
# Deactivate current environment
deactivate

# Remove and recreate environment
rm -rf lab02_env
python3 -m venv lab02_env
source lab02_env/bin/activate
pip install requests beautifulsoup4 pandas matplotlib
```

## 📝 Output File Formats

### CSV Files
All CSV files follow consistent formatting:
- UTF-8 encoding
- Comma-separated values
- Headers in first row
- Timestamps in YYYY-MM-DD HH:MM:SS format

### JSON Files
Raw API responses preserved for:
- Data backup
- Advanced analysis
- API debugging

## 🤝 Contributing

To extend this project:

1. **Add new data sources**: Follow the existing pattern in each directory
2. **Enhance visualizations**: Modify chart generation functions
3. **Add new cryptocurrencies**: Update symbol lists in crypto trackers
4. **Improve alerts**: Enhance threshold logic or notification methods

## 📄 License

This project is for educational purposes as part of Lab02 coursework.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in terminal output
3. Ensure all dependencies are installed
4. Verify internet connectivity for API calls

---

**Happy Data Collecting! 📊🚀**
