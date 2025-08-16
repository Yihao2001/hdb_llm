import json
import requests
import os
import uvicorn
import threading
import joblib
import logging
import time
import pandas as pd
import sqlite3

from fastapi import FastAPI, Request
from pydantic import BaseModel
from pathlib import Path
from openai import OpenAI
from typing import Optional
from datetime import datetime


OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY)

logging.basicConfig(
    filename="api_requests.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_DIR = Path(__file__).resolve().parent.parent
model_folder = BASE_DIR / "backend"
DB_PATH = BASE_DIR / "db/hdb_data.db" 
model_files = list(model_folder.glob("price_model_v*.pkl"))
if not model_files:
    raise FileNotFoundError(f"No model files found in {model_folder}!")

if not model_files:
    raise FileNotFoundError("No model files found!")

model_files.sort(reverse=True)
latest_model_file = model_files[0]
model = joblib.load(latest_model_file)
MODEL_VERSION = latest_model_file.name

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # to return dict-like rows
    return conn

def query_db(query: str, params: Optional[tuple] = ()):
    conn = get_db_connection()
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

app = FastAPI()
REQUEST_COUNT = 0
ERROR_COUNT = 0

class InputData(BaseModel):
    town: str
    flat_type: str
    storey_range: str
    floor_area_sqm: int
    flat_model: str
    remaining_lease: int
    discount: float

class AgentRequest(BaseModel):
    user_query: str

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    global REQUEST_COUNT, ERROR_COUNT
    start_time = time.time()
    REQUEST_COUNT += 1
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            ERROR_COUNT += 1
    except Exception as e:
        ERROR_COUNT += 1
        logging.error(f"Request error: {e}")
        raise
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/metrics")
def get_metrics():
    return {
        "request_count": REQUEST_COUNT,
        "error_count": ERROR_COUNT,
        "model_version": MODEL_VERSION
    }

@app.post("/predict_price")
def predict_price(data: InputData):
    df_input = pd.DataFrame([data.model_dump()])

    pred = model.predict(df_input)
    predicted_price = round(float(pred[0]), 2)
    discounted_price = round(predicted_price * data.discount / 100.0, 2)

    logging.info(f"Input: {data.model_dump()}, Predicted: {predicted_price}, Model: {MODEL_VERSION}")

    return {
        "predicted_price": predicted_price,
        "disounted_price": discounted_price,
        "model_version": MODEL_VERSION
    }

@app.get("/bto/town_reco")
def get_street_frequency(type:str="highest", duration:int=10, limit:int=1):
    current_year = datetime.now().year
    year_cutoff = current_year - duration
    print(type)
    order = "DESC" if type == "highest" else "ASC"
    query = f"""
        SELECT bldg_contract_town, COUNT(*) as launch_count
        FROM bto_launches
        WHERE year_completed >= {year_cutoff}
        GROUP BY bldg_contract_town
        ORDER BY launch_count {order}
        LIMIT {limit}
    """

    result = query_db(query)
    if not result:
        return {"message": "No BTO data found for the last 10 years."}
    return result[0]

@app.post("/agent")
def agent_request(req: AgentRequest):
    user_query = req.user_query
    BASE_URL = "http://localhost:8000"
    planner_prompt = f"""
    The user asked: {user_query}
    You are connected to 2 APIs:
    - GET /bto/town_reco (params: type [highest|lowest], duration [int years], limit [int])
    - POST /predict_price 
      (params:
            "town": str,
            "flat_type": str,
            "storey_range": str,
            "floor_area_sqm": int,
            "flat_model": str,
            "remaining_lease": int
            "discount": float
      )
    
    Break down the query into steps:
    1. Decide which towns to fetch with /bto/town_reco.
    2. For each town, call /predict_price based on town recommended from get request, for any params not specified by user prompt, use the following defaults:
        - "town": "ANG MO KIO"
        - "flat_type": "4 ROOM,
        - "storey_range": "10 TO 12",
        - "floor_area_sqm": 92,
        - "flat_model": "New generation",
        - "remaining_lease": 80
        - "discount": 20
    3. Return the results as JSON.
    
    Respond ONLY in JSON format: a list of actions with {{"action": "GET"/"POST", "endpoint": "...", "params": {{...}}}}
    """

    plan = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": planner_prompt}],
        temperature=0,
        response_format={ "type": "json_object" }
    )

    actions = json.loads(plan.choices[0].message.content)["actions"]

    results = []
    for act in actions:
        if act["action"] == "GET":
            resp = requests.get(BASE_URL + act["endpoint"], params=act["params"]).json()
        elif act["action"] == "POST":
            resp = requests.post(BASE_URL + act["endpoint"], json=act["params"]).json()
        results.append({"action": act, "result": resp})

    summary_prompt = f"""
    User query: {user_query}
    Here are the raw results: {json.dumps(results, indent=2)}
    
    Please provide a structured housing analysis:
    - Recommended estates
    - Price insights
    - Suggested household income brackets
    """

    summary = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.5
    )

    return {
        "summary": summary.choices[0].message.content,
        "plan": actions,
        "results": results
    }

# ---------- Startup logic ----------
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

def interactive_client():
    time.sleep(2)
    while True:
        user_input = input("\nEnter your housing query (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        resp = requests.post("http://127.0.0.1:8000/agent", json={"user_query": user_input})
        print("\n=== Response ===")
        print(resp.json())


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    interactive_client()