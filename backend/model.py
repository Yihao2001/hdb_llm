import joblib
import datetime
import sqlite3
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "../db/hdb_data.db"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT town, flat_type, storey_range, floor_area_sqm, flat_model, remaining_lease, resale_price FROM resale_prices", conn)
conn.close()

X = df.drop(columns=['resale_price'])
y = df['resale_price']

categorical_cols = ['town', 'flat_type', 'storey_range', 'flat_model']
numerical_cols = ['floor_area_sqm', 'remaining_lease']

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ],
    remainder='passthrough'  # keep numerical columns
)

model = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

model.fit(X, y)

# Model versioning: timestamped
version = datetime.datetime.now().strftime("%Y%m%d%H%M")
model_filename = f"price_model_v{version}.pkl"
joblib.dump(model, model_filename)
print(f"Model trained and saved as {model_filename}")
