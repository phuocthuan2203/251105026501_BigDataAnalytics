import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time

def get_bitcoin_current_price():
    """Get current Bitcoin price from CoinGecko API"""
    print("₿ Fetching current Bitcoin price...")
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
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
        
        price = data["bitcoin"]["usd"]
        timestamp = data["bitcoin"]["last_updated_at"]
        
        # Convert timestamp to readable format
        readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"✅ Current Bitcoin price: ${price:,.2f} USD (as of {readable_time})")
        return price, readable_time, timestamp
        
    except Exception as e:
        print(f"❌ Error fetching current Bitcoin price: {e}")
        return None, None, None

def get_bitcoin_multiple_samples(samples=10, interval_seconds=30):
    """Get multiple Bitcoin price samples over time"""
    print(f"📈 Collecting {samples} Bitcoin price samples (every {interval_seconds} seconds)...")
    
    price_data = []
    
    for i in range(samples):
        print(f"📊 Sample {i+1}/{samples}...")
        price, readable_time, _ = get_bitcoin_current_price()
        
        if price is not None:
            price_data.append({
                "time": readable_time,
                "usd_price": price
            })
        
        # Wait before next sample (except for the last one)
        if i < samples - 1:
            print(f"⏳ Waiting {interval_seconds} seconds...")
            time.sleep(interval_seconds)
    
    if price_data:
        df = pd.DataFrame(price_data)
        print(f"✅ Collected {len(df)} price samples")
        return df
    else:
        print("❌ No price samples collected")
        return None

def collect_bitcoin_price_series(interval_minutes=5, duration_minutes=30):
    """Collect Bitcoin prices at regular intervals"""
    print(f"⏰ Starting Bitcoin price collection every {interval_minutes} minutes for {duration_minutes} minutes...")
    
    price_data = []
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    collection_count = 0
    while datetime.now() < end_time:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        price, _, _ = get_bitcoin_current_price()
        
        if price is not None:
            price_data.append({
                "time": current_time,
                "usd_price": price
            })
            collection_count += 1
            print(f"📊 Collected #{collection_count}: ${price:,.2f} at {current_time}")
        
        # Wait for next interval (unless it's the last iteration)
        if datetime.now() + timedelta(minutes=interval_minutes) < end_time:
            print(f"⏳ Waiting {interval_minutes} minutes for next collection...")
            time.sleep(interval_minutes * 60)
        else:
            break
    
    if price_data:
        df = pd.DataFrame(price_data)
        print(f"✅ Completed price series collection: {len(df)} records")
        return df
    else:
        print("❌ No price data collected")
        return None

def main():
    """Main function to collect Bitcoin price data"""
    print("₿ Bitcoin Price Tracker")
    print("=" * 50)
    
    all_price_data = []
    
    # Option 1: Get current price
    print("\n1️⃣ Getting current Bitcoin price...")
    current_price, current_time, _ = get_bitcoin_current_price()
    if current_price is not None:
        all_price_data.append({
            "time": current_time,
            "usd_price": current_price
        })
    
    # Option 2: Get multiple price samples (5 samples, 10 seconds apart)
    print("\n2️⃣ Getting multiple Bitcoin price samples...")
    samples_df = get_bitcoin_multiple_samples(samples=5, interval_seconds=10)
    if samples_df is not None:
        all_price_data.extend(samples_df.to_dict('records'))
    
    # Option 3: Collect real-time prices (uncomment if you want live collection)
    # print("\n3️⃣ Collecting real-time Bitcoin prices...")
    # realtime_df = collect_bitcoin_price_series(interval_minutes=1, duration_minutes=5)
    # if realtime_df is not None:
    #     all_price_data.extend(realtime_df.to_dict('records'))
    
    if all_price_data:
        # Create final DataFrame
        final_df = pd.DataFrame(all_price_data)
        
        # Remove duplicates and sort by time
        final_df = final_df.drop_duplicates(subset=['time']).sort_values('time').reset_index(drop=True)
        
        # Add collection metadata
        collection_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        final_df['collected_at'] = collection_timestamp
        
        # Save to CSV (same name as Python file)
        base_filename = "bitcoin_price_tracker"
        csv_filename = f"{base_filename}.csv"
        
        # Save main CSV with just time and USD price
        main_df = final_df[['time', 'usd_price']].copy()
        main_df.to_csv(csv_filename, index=False, encoding="utf-8")
        print(f"📊 Saved Bitcoin prices to: {csv_filename}")
        
        # Save detailed CSV with metadata
        detailed_csv = f"{base_filename}_detailed.csv"
        final_df.to_csv(detailed_csv, index=False, encoding="utf-8")
        print(f"📊 Saved detailed data to: {detailed_csv}")
        
        # Save raw JSON data
        raw_data = {
            "collection_info": {
                "script": "bitcoin_price_tracker.py",
                "collection_time": collection_timestamp,
                "total_records": len(final_df)
            },
            "price_data": final_df.to_dict('records')
        }
        json_file = f"{base_filename}_raw.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        print(f"📊 Saved raw data to: {json_file}")
        
        # Display summary
        print("\n📈 Bitcoin Price Summary:")
        print(f"   💰 Total records: {len(main_df)}")
        print(f"   📅 Time range: {main_df['time'].min()} to {main_df['time'].max()}")
        print(f"   💵 Price range: ${main_df['usd_price'].min():,.2f} - ${main_df['usd_price'].max():,.2f}")
        print(f"   📊 Average price: ${main_df['usd_price'].mean():,.2f}")
        print(f"   🕐 Collection time: {collection_timestamp}")
        
        # Display sample data
        print("\n💰 Sample Bitcoin Price Data:")
        print(main_df[['time', 'usd_price']].head(8).to_string(index=False))
        
        # Price analysis
        if len(main_df) > 1:
            price_change = main_df['usd_price'].iloc[-1] - main_df['usd_price'].iloc[0]
            price_change_pct = (price_change / main_df['usd_price'].iloc[0]) * 100
            
            print(f"\n📊 Price Analysis:")
            print(f"   🔄 Price change: ${price_change:+,.2f} ({price_change_pct:+.2f}%)")
            print(f"   📈 Highest: ${main_df['usd_price'].max():,.2f}")
            print(f"   📉 Lowest: ${main_df['usd_price'].min():,.2f}")
            print(f"   📊 Volatility (std): ${main_df['usd_price'].std():.2f}")
        
        return main_df
    
    else:
        print("❌ No Bitcoin price data collected")
        return None

if __name__ == "__main__":
    bitcoin_data = main()
    
    if bitcoin_data is not None:
        print(f"\n🎉 Bitcoin price collection completed successfully!")
        print(f"📁 Files saved in current directory with base name 'bitcoin_price_tracker'")
    else:
        print("\n😞 Bitcoin price collection failed. Please check the error messages above.")
