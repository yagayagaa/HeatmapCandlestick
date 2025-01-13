# Import necessary libraries
import pandas as pd  # For handling and manipulating CSV data
import matplotlib  # For plotting visualizations
matplotlib.use('TkAgg')  # Use the TkAgg backend for interactive plotting
import matplotlib.pyplot as plt  # Provides MATLAB-like plotting functionality
import seaborn as sns  # Advanced visualization library (used for heatmaps)
import matplotlib.ticker as ticker  # For customizing tick marks on axes
import matplotlib.colors as mcolors  # For creating custom colormaps

# Define file paths for input CSV data
bids_file = 'bids.csv'  # Path to the bids CSV file
asks_file = 'asks.csv'  # Path to the asks CSV file

# Load the CSV file
file_path = 'ohlc_data.csv'

# Load CSV files into Pandas DataFrames
bids_df = pd.read_csv(bids_file, index_col='time')  # Load bids CSV with 'time' as the index
asks_df = pd.read_csv(asks_file, index_col='time')  # Load asks CSV with 'time' as the index

df = pd.read_csv(file_path)
# Ensure 'time' column is in datetime format
df['time'] = pd.to_datetime(df['time'])

# Ensure that all price columns and quantities are numeric
bids_df.columns = bids_df.columns.astype(float)  # Convert bid price levels to floats
asks_df.columns = asks_df.columns.astype(float)  # Convert ask price levels to floats
bids_df = bids_df.apply(pd.to_numeric, errors='coerce')  # Convert bid quantities to numeric, replacing non-numeric values with NaN
asks_df = asks_df.apply(pd.to_numeric, errors='coerce')  # Convert ask quantities to numeric, replacing non-numeric values with NaN

# Ensure the 'time' index is in datetime format for both DataFrames
bids_df.index = pd.to_datetime(bids_df.index)  # Convert 'time' to a datetime object in bids_df
asks_df.index = pd.to_datetime(asks_df.index)  # Convert 'time' to a datetime object in asks_df

# Sort the DataFrames by time and prices
bids_df = bids_df.sort_index()  # Sort bids DataFrame by the 'time' index
asks_df = asks_df.sort_index()  # Sort asks DataFrame by the 'time' index
bids_df = bids_df.reindex(sorted(bids_df.columns, reverse=True), axis=1)  # Sort bid prices in descending order (highest price first)
asks_df = asks_df.reindex(sorted(asks_df.columns), axis=1)  # Sort ask prices in ascending order (lowest price first)

# Define the price range for visualization
price_min = 20000  # Minimum price to include in the heatmap
price_max = 150000  # Maximum price to include in the heatmap
tick_size = 5000  # Interval between y-axis ticks (price levels)

# Create a unified list of price levels within the defined range
all_prices = [price for price in sorted(set(bids_df.columns).union(asks_df.columns)) if price_min <= price <= price_max]

# Filter and adjust DataFrames to match the price range
bids_df = bids_df.reindex(columns=all_prices, fill_value=0)  # Keep only relevant bid price levels, filling missing ones with 0
asks_df = asks_df.reindex(columns=all_prices, fill_value=0)  # Keep only relevant ask price levels, filling missing ones with 0

# Define the range for heatmap legends
bids_legend_min = 0  # Minimum value for the bids heatmap legend
bids_legend_max = 30000  # Maximum value for the bids heatmap legend
asks_legend_min = 0  # Minimum value for the asks heatmap legend
asks_legend_max = 15000  # Maximum value for the asks heatmap legend

# Create a custom colormap for the heatmaps
custom_cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", ["white", "red", "yellow", "green", "blue"])

# Create a new figure and axis for the heatmaps
fig, ax = plt.subplots(figsize=(16, 10))  # Set the plot size to 16x10 inches

# Plot the heatmap for asks (in red shades)
sns.heatmap(
    asks_df.T,  # Transpose DataFrame for heatmap
    cmap=custom_cmap,  # Use the custom colormap
    mask=(asks_df == 0).T,  # Mask out values where quantity is 0
    cbar_kws={  # Customize the colorbar
        'label': 'Asks (Accumulated Quantities)',  # Label for the colorbar
        'format': ticker.FuncFormatter(lambda x, _: f"{x:,.0f}")  # Format colorbar values with commas
    },
    ax=ax,  # Plot on the same axis
    vmin=asks_legend_min, vmax=asks_legend_max  # Set the legend range
)

# Plot the heatmap for bids (in green shades)
sns.heatmap(
    bids_df.T,  # Transpose DataFrame for heatmap
    cmap=custom_cmap,  # Use the custom colormap
    mask=(bids_df == 0).T,  # Mask out values where quantity is 0
    cbar_kws={  # Customize the colorbar
        'label': 'Bids (Accumulated Quantities)',  # Label for the colorbar
        'format': ticker.FuncFormatter(lambda x, _: f"{x:,.0f}")  # Format colorbar values with commas
    },
    ax=ax,  # Plot on the same axis
    vmin=bids_legend_min, vmax=bids_legend_max  # Set the legend range
)

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

# Set y-axis ticks based on the defined price range and interval
y_ticks = [price for price in range(price_min, price_max + tick_size, tick_size)]  # Generate tick intervals
ax.set_yticks([all_prices.index(price) for price in y_ticks if price in all_prices])  # Set tick positions
ax.set_yticklabels([f"{price:,}" for price in y_ticks if price in all_prices])  # Format tick labels with commas

# Add horizontal gridlines for each price level
for y_tick in [all_prices.index(price) for price in y_ticks if price in all_prices]:
    ax.axhline(y=y_tick, color='black', linewidth=0.5, linestyle='-')  # Add a thin black line at each price level

# Reverse the y-axis to display higher prices at the top
ax.invert_yaxis()

# Format the x-axis for time
daily_ticks = bids_df.index[bids_df.index.hour == 0]  # Select timestamps that occur at midnight
ax.set_xticks(range(0, len(bids_df.index), 24))  # Set x-axis tick positions for daily intervals
ax.set_xticklabels(daily_ticks.strftime("%Y-%m-%d"), rotation=45, ha="right")  # Format tick labels as dates

# Customize the plot with titles and labels
ax.set_title("Depth of Market (DOM) Heatmap for Bids and Asks")  # Add a title
ax.set_xlabel("Time")  # Label the x-axis
ax.set_ylabel("Price")  # Label the y-axis

# Adjust the layout to prevent overlap
plt.tight_layout()

# Display the heatmap
plt.show()
