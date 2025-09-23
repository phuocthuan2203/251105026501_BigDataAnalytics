import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time

# Price thresholds for warnings
PRICE_THRESHOLDS = {
    "BTC": {
        "high": 113000,  # Warning if Bitcoin goes above $113,000 (lowered to trigger alert)
        "low": 110000    # Warning if Bitcoin goes below $110,000
    },
    "ETH": {
        "high": 4100,    # Warning if Ethereum goes above $4,100 (lowered to trigger alert)
        "low": 4000      # Warning if Ethereum goes below $4,000
    },
    "DOGE": {
        "high": 0.23,    # Warning if Dogecoin goes above $0.23 (lowered to trigger alert)
        "low": 0.20      # Warning if Dogecoin goes below $0.20
    }
}

def check_price_thresholds(symbol, price):
    """Check if price exceeds predefined thresholds and return warning message"""
    warnings = []
    
    if symbol in PRICE_THRESHOLDS:
        thresholds = PRICE_THRESHOLDS[symbol]
        
        if price > thresholds["high"]:
            warnings.append(f"🚨 HIGH ALERT: {symbol} price ${price:,.2f} is above threshold ${thresholds['high']:,.2f}")
        elif price < thresholds["low"]:
            warnings.append(f"⚠️ LOW ALERT: {symbol} price ${price:,.2f} is below threshold ${thresholds['low']:,.2f}")
        else:
            warnings.append(f"✅ NORMAL: {symbol} price ${price:,.2f} is within safe range (${thresholds['low']:,.2f} - ${thresholds['high']:,.2f})")
    
    return warnings

def display_threshold_settings():
    """Display current price threshold settings"""
    print("\n⚙️ Current Price Threshold Settings:")
    print("-" * 45)
    for symbol, thresholds in PRICE_THRESHOLDS.items():
        print(f"{symbol:>4}: Low ${thresholds['low']:>8,.2f} | High ${thresholds['high']:>8,.2f}")
    print("-" * 45)

def get_multiple_crypto_prices(crypto_symbols=None):
    """Get current prices for multiple cryptocurrencies from CoinGecko API"""
    if crypto_symbols is None:
        crypto_symbols = ["bitcoin", "ethereum", "dogecoin"]
    
    print(f"💰 Fetching prices for: {', '.join(crypto_symbols).upper()}...")
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(crypto_symbols),
        "vs_currencies": "usd",
        "include_last_updated_at": "true"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        crypto_data = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        all_warnings = []
        
        # Map crypto IDs to symbols
        crypto_map = {
            "bitcoin": "BTC",
            "ethereum": "ETH", 
            "dogecoin": "DOGE"
        }
        
        for crypto_id in crypto_symbols:
            if crypto_id in data:
                price = data[crypto_id]["usd"]
                symbol = crypto_map.get(crypto_id, crypto_id.upper())
                
                crypto_data.append({
                    "time": current_time,
                    "symbol": symbol,
                    "usd_price": price
                })
                
                print(f"✅ {symbol}: ${price:,.2f} USD")
                
                # Check price thresholds
                warnings = check_price_thresholds(symbol, price)
                all_warnings.extend(warnings)
        
        # Display all warnings
        if all_warnings:
            print("\n🔔 Price Threshold Alerts:")
            for warning in all_warnings:
                print(f"   {warning}")
        
        return crypto_data, data
        
    except Exception as e:
        print(f"❌ Error fetching crypto prices: {e}")
        return None, None

def get_crypto_samples_over_time(samples=5, interval_seconds=30, crypto_symbols=None):
    """Collect multiple cryptocurrency price samples over time"""
    if crypto_symbols is None:
        crypto_symbols = ["bitcoin", "ethereum", "dogecoin"]
    
    print(f"📈 Collecting {samples} price samples for multiple cryptos (every {interval_seconds} seconds)...")
    
    all_crypto_data = []
    
    for i in range(samples):
        print(f"\n📊 Sample {i+1}/{samples}...")
        crypto_data, _ = get_multiple_crypto_prices(crypto_symbols)
        
        if crypto_data:
            all_crypto_data.extend(crypto_data)
        
        # Wait before next sample (except for the last one)
        if i < samples - 1:
            print(f"⏳ Waiting {interval_seconds} seconds...")
            time.sleep(interval_seconds)
    
    if all_crypto_data:
        df = pd.DataFrame(all_crypto_data)
        print(f"\n✅ Collected {len(df)} total price records")
        return df
    else:
        print("❌ No crypto price samples collected")
        return None

def analyze_crypto_data(df):
    """Analyze cryptocurrency price data"""
    print("\n📊 Cryptocurrency Analysis:")
    
    # Group by symbol for analysis
    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol].copy()
        symbol_data = symbol_data.sort_values('time')
        
        if len(symbol_data) > 1:
            first_price = symbol_data['usd_price'].iloc[0]
            last_price = symbol_data['usd_price'].iloc[-1]
            price_change = last_price - first_price
            price_change_pct = (price_change / first_price) * 100
            
            print(f"   {symbol}:")
            print(f"     💵 Price range: ${symbol_data['usd_price'].min():,.2f} - ${symbol_data['usd_price'].max():,.2f}")
            print(f"     📊 Average: ${symbol_data['usd_price'].mean():,.2f}")
            print(f"     🔄 Change: ${price_change:+,.2f} ({price_change_pct:+.2f}%)")
            print(f"     📈 Volatility: ${symbol_data['usd_price'].std():.2f}")
        else:
            print(f"   {symbol}: ${symbol_data['usd_price'].iloc[0]:,.2f} (single sample)")

def create_crypto_comparison_chart(df):
    """Create a simple text-based comparison chart"""
    print("\n📊 Price Comparison Chart:")
    print("-" * 50)
    
    # Get latest prices for each crypto
    latest_prices = df.groupby('symbol')['usd_price'].last().sort_values(ascending=False)
    
    max_price = latest_prices.max()
    
    for symbol, price in latest_prices.items():
        # Create a simple bar chart using characters
        bar_length = int((price / max_price) * 30)
        bar = "█" * bar_length
        print(f"{symbol:>4}: {bar} ${price:,.2f}")

def save_threshold_alerts(df, base_filename):
    """Save threshold alerts to a separate file"""
    alerts = []
    
    for _, row in df.iterrows():
        symbol = row['symbol']
        price = row['usd_price']
        time = row['time']
        
        if symbol in PRICE_THRESHOLDS:
            thresholds = PRICE_THRESHOLDS[symbol]
            alert_type = "NORMAL"
            
            if price > thresholds["high"]:
                alert_type = "HIGH_ALERT"
            elif price < thresholds["low"]:
                alert_type = "LOW_ALERT"
            
            alerts.append({
                "time": time,
                "symbol": symbol,
                "price": price,
                "alert_type": alert_type,
                "threshold_low": thresholds["low"],
                "threshold_high": thresholds["high"]
            })
    
    if alerts:
        alerts_df = pd.DataFrame(alerts)
        alerts_filename = f"{base_filename}_alerts.csv"
        alerts_df.to_csv(alerts_filename, index=False, encoding="utf-8")
        print(f"🚨 Saved threshold alerts to: {alerts_filename}")
        
        # Count alerts by type
        alert_counts = alerts_df['alert_type'].value_counts()
        print(f"📊 Alert Summary: {dict(alert_counts)}")
        
        return alerts_df
    
    return None

def main():
    """Main function to track multiple cryptocurrencies"""
    print("🚀 Multi-Cryptocurrency Tracker")
    print("=" * 50)
    
    # Define cryptocurrencies to track
    crypto_symbols = ["bitcoin", "ethereum", "dogecoin"]
    crypto_names = ["BTC", "ETH", "DOGE"]
    
    print(f"📋 Tracking: {', '.join(crypto_names)}")
    
    # Display threshold settings
    display_threshold_settings()
    
    all_crypto_data = []
    
    # Option 1: Get current prices for all cryptos
    print("\n1️⃣ Getting current cryptocurrency prices...")
    current_prices, raw_data = get_multiple_crypto_prices(crypto_symbols)
    if current_prices:
        all_crypto_data.extend(current_prices)
    
    # Option 2: Get multiple samples over time
    print("\n2️⃣ Collecting price samples over time...")
    samples_df = get_crypto_samples_over_time(samples=3, interval_seconds=15, crypto_symbols=crypto_symbols)
    if samples_df is not None:
        all_crypto_data.extend(samples_df.to_dict('records'))
    
    if all_crypto_data:
        # Create final DataFrame
        final_df = pd.DataFrame(all_crypto_data)
        
        # Remove duplicates and sort
        final_df = final_df.drop_duplicates(subset=['time', 'symbol']).sort_values(['time', 'symbol']).reset_index(drop=True)
        
        # Add collection metadata
        collection_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        final_df['collected_at'] = collection_timestamp
        
        # Save to CSV files (same name as Python file)
        base_filename = "multi_crypto_tracker"
        
        # Main CSV with time, symbol, and USD price
        main_csv = f"{base_filename}.csv"
        main_df = final_df[['time', 'symbol', 'usd_price']].copy()
        main_df.to_csv(main_csv, index=False, encoding="utf-8")
        print(f"📊 Saved crypto prices to: {main_csv}")
        
        # Detailed CSV with metadata
        detailed_csv = f"{base_filename}_detailed.csv"
        final_df.to_csv(detailed_csv, index=False, encoding="utf-8")
        print(f"📊 Saved detailed data to: {detailed_csv}")
        
        # Save raw JSON data
        raw_data_export = {
            "collection_info": {
                "script": "multi_crypto_tracker.py",
                "collection_time": collection_timestamp,
                "cryptocurrencies": crypto_names,
                "total_records": len(final_df)
            },
            "price_data": final_df.to_dict('records'),
            "raw_api_response": raw_data if raw_data else {}
        }
        json_file = f"{base_filename}_raw.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(raw_data_export, f, ensure_ascii=False, indent=2)
        print(f"📊 Saved raw data to: {json_file}")
        
        # Display summary
        print("\n📈 Multi-Crypto Summary:")
        print(f"   💰 Cryptocurrencies tracked: {len(main_df['symbol'].unique())}")
        print(f"   📊 Total records: {len(main_df)}")
        print(f"   📅 Time range: {main_df['time'].min()} to {main_df['time'].max()}")
        print(f"   🕐 Collection time: {collection_timestamp}")
        
        # Display sample data
        print("\n💰 Sample Cryptocurrency Data:")
        print(main_df.head(10).to_string(index=False))
        
        # Analyze the data
        analyze_crypto_data(main_df)
        
        # Create comparison chart
        create_crypto_comparison_chart(main_df)
        
        # Save threshold alerts
        alerts_df = save_threshold_alerts(main_df, base_filename)
        
        # Summary by cryptocurrency
        print("\n📋 Summary by Cryptocurrency:")
        crypto_summary = main_df.groupby('symbol').agg({
            'usd_price': ['count', 'mean', 'min', 'max', 'std']
        }).round(2)
        crypto_summary.columns = ['samples', 'avg_price', 'min_price', 'max_price', 'volatility']
        print(crypto_summary.to_string())
        
        return main_df
    
    else:
        print("❌ No cryptocurrency data collected")
        return None

if __name__ == "__main__":
    crypto_data = main()
    
    if crypto_data is not None:
        print(f"\n🎉 Multi-cryptocurrency tracking completed successfully!")
        print(f"📁 Files saved in current directory with base name 'multi_crypto_tracker'")
        print(f"💡 Tracked: BTC, ETH, DOGE with time-series data")
    else:
        print("\n😞 Multi-cryptocurrency tracking failed. Please check the error messages above.")
