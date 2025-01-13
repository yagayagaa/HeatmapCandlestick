import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the CSV file
file_path = 'ohlc_data.csv'
df = pd.read_csv(file_path)

# Ensure 'time' column is in datetime format
df['time'] = pd.to_datetime(df['time'])

# Plot the candlestick chart manually
fig, ax = plt.subplots(figsize=(14, 8))

for idx, row in df.iterrows():
    # Determine the color of the candle
    color = 'green' if row['c'] >= row['o'] else 'red'
    
    # Plot the upper wick (from max(open, close) to high)
    ax.plot([row['time'], row['time']], [max(row['o'], row['c']), row['h']], color='black', linewidth=1)
    # Plot the lower wick (from min(open, close) to low)
    ax.plot([row['time'], row['time']], [min(row['o'], row['c']), row['l']], color='black', linewidth=1)
    
    # Plot the candle body
    ax.bar(row['time'], height=abs(row['c'] - row['o']), bottom=min(row['o'], row['c']),
           width=0.5, color=color, edgecolor='black')  # Candle body

# Formatting the x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.set_xlabel("Time (ISO)")
ax.set_ylabel("Price")
plt.xticks(rotation=45)
plt.title("Enhanced Candlestick Chart for BTC/USDT (Proper Wicks)")
plt.grid(True)
plt.tight_layout()
plt.show()
