import sqlite3
import pandas as pd

# Extract CSVs
resale_df_1 = pd.read_csv("data/resale_prices_1.csv")
resale_df_2 = pd.read_csv("data/resale_prices_2.csv")
bto_df = pd.read_csv("data/bto_info.csv")

# Transform
resale_df_2['remaining_lease'] = resale_df_2['remaining_lease'].str[:2].astype(int)
resale_df_combined = pd.concat([resale_df_1, resale_df_2], ignore_index=True)

town_mapping = {
    'AMK': 'ANG MO KIO', 'BB': 'BUKIT BATOK', 'BD': 'BEDOK', 'BH': 'BISHAN',
    'BM': 'BUKIT MERAH', 'BP': 'BUKIT PANJANG', 'BT': 'BUKIT TIMAH',
    'CCK': 'CHOA CHU KANG', 'CL': 'CLEMENTI', 'CT': 'CENTRAL AREA',
    'GL': 'GEYLANG', 'HG': 'HOUGANG', 'JE': 'JURONG EAST',
    'JW': 'JURONG WEST', 'KWN': 'KALLANG/WHAMPOA', 'MP': 'MARINE PARADE',
    'PG': 'PUNGGOL', 'PRC': 'PASIR RIS', 'QT': 'QUEENSTOWN',
    'SB': 'SEMBAWANG', 'SGN': 'SERANGOON', 'SK': 'SENGKANG',
    'TAP': 'TAMPINES', 'TG': 'TENGAH', 'TP': 'TOA PAYOH',
    'WL': 'WOODLANDS', 'YS': 'YISHUN'
}
bto_df['bldg_contract_town'] = bto_df['bldg_contract_town'].replace(town_mapping)

# Connect to SQLite
conn = sqlite3.connect("db/hdb_data.db")

# Load into database
resale_df_combined.to_sql("resale_prices", conn, if_exists="replace", index=False)
bto_df.to_sql("bto_launches", conn, if_exists="replace", index=False)

conn.close()

print("CSV data loaded into database.")
