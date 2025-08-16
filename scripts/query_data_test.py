import sqlite3

conn = sqlite3.connect("db/hdb_data.db")
cur = conn.cursor()

# Example: Get first 5 resale records
for row in cur.execute("SELECT * FROM resale_prices LIMIT 5;"):
    print(row)

for row in cur.execute("SELECT * FROM bto_launches LIMIT 5;"):
    print(row)

conn.close()

