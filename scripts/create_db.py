import sqlite3

# Connect to SQLite (will create file if not exists)
conn = sqlite3.connect("db/hdb_data.db")
cursor = conn.cursor()

# Create table for BTO 
cursor.execute("""
CREATE TABLE IF NOT EXISTS bto_launches (
    blk_no TEXT,
    street TEXT,
    max_floor_lvl INTEGER,
    year_completed INTEGER,
    residential TEXT,
    commercial TEXT,
    market_hawker TEXT,
    miscellaneous TEXT,
    multistorey_carpark TEXT,
    precinct_pavilion TEXT,
    bldg_contract_town TEXT,
    total_dwelling_units INTEGER,
    room_1_sold INTEGER,
    room_2_sold INTEGER,
    room_3_sold INTEGER,
    room_4_sold INTEGER,
    room_5_sold INTEGER,
    exec_sold INTEGER,
    multigen_sold INTEGER,
    studio_apartment_sold INTEGER,
    room_1_rental INTEGER,
    room_2_rental INTEGER,
    room_3_rental INTEGER,
    other_room_rental INTEGER
);
""")

# Create table for resale prices
cursor.execute("""
CREATE TABLE IF NOT EXISTS resale_prices (
    month TEXT,
    town TEXT,
    flat_type TEXT,
    block TEXT,
    street_name TEXT,
    storey_range TEXT,
    floor_area_sqm INTEGER,
    flat_model TEXT,
    lease_commence_date INTEGER,
    remaining_lease INTEGER,
    resale_price INTEGER
);
""")

conn.commit()

print("✅ Database and tables created successfully!")
