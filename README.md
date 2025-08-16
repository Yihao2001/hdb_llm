# AI Housing Agent API

This repository provides an LLM-powered system that allows users to query housing recommendations and resale price predictions. It combines a simple multivariate regression model, a SQLite database, and an agent LLM that orchestrates API calls based on natural language prompts.

---

## Table of Contents

1. [Setup](#setup)
2. [Architecture](#architecture)
   - [Database](#database)
   - [Model](#model)
   - [API Endpoints](#api-endpoints)
   - [Agent LLM](#agent-llm)
   - [Monitoring & Operational Processes](#monitoring--operational-processes)

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd <repo-folder>
```

### 2. Set up a Python virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the backend API and interactive prompt

```bash
python backend/api.py
```

Once the server is running, enter a housing query at the prompt. The agent LLM will process your query and provide structured results.

---

## Architecture

The system is designed for simplicity, clarity, and easy operational monitoring.

### Database

- **Type:** SQLite
- **Purpose:** Stores housing resale price data (`resale_prices`) and BTO launch data (`bto_launches`)
- **Rationale:** The dataset is small, so a lightweight, file-based database is sufficient

### Model

- **Type:** Multivariate Linear Regression using scikit-learn pipeline
- **Input Features:** `town`, `flat_type`, `storey_range`, `floor_area_sqm`, `flat_model`, `remaining_lease`
- **Target:** `resale_price`

#### Processing

- Categorical features are one-hot encoded
- Numerical features are passed through as-is

#### Versioning

Each trained model is saved with a timestamped filename (`price_model_vYYYYMMDDHHMM.pkl`)

#### Use Case

Provides resale price predictions and supports discount adjustments for user queries.

### API Endpoints

#### `POST /agent`

- Accepts a natural language query
- The agent LLM decides which endpoint(s) to call and orchestrates the process
- Returns structured JSON results with recommendations and price insights

#### `POST /predict_price`

- Accepts detailed housing parameters (town, flat type, floor area, etc.)
- Returns predicted resale price and discounted price based on user input

#### `GET /bto/town_reco`

Provides recommendations for towns based on BTO launch frequency.

**Supports parameters:**
- `type`: `highest` or `lowest` launches
- `duration`: number of years to look back
- `limit`: number of towns to return

#### `GET /metrics`

Returns operational metrics:
- `request_count`
- `error_count`
- `model_version`

### Agent LLM

- **Role:** Acts as the orchestrator for user prompts

#### Workflow

1. Receives natural language query
2. Breaks it into structured steps
3. Determines which API endpoints to call
4. Executes calls with default values if user parameters are missing
5. Aggregates results and produces a summary

- **LLM Model:** gpt-4o-mini via OpenAI API

### Monitoring & Operational Processes

#### Logging

All API requests and model predictions are logged.

#### Metrics Tracking

Tracks total requests, errors, and current model version.

#### Automated Testing

Includes:
- Unit tests for endpoints
- Edge case tests for prediction inputs
- LLM plan validation

#### Operational Best Practices

- Model versioning ensures reproducibility
- Edge case handling for missing user inputs
- Continuous monitoring of API responses and LLM actions

---

## Usage Examples

### Example 1: Natural Language Query

```bash
# Start the API server
python backend/api.py

# Enter a query like:
"I'm looking for a 4-room flat in Tampines with good resale value"
```

### Example 2: Direct Price Prediction

```bash
curl -X POST http://localhost:5000/predict_price \
  -H "Content-Type: application/json" \
  -d '{
    "town": "Tampines",
    "flat_type": "4 ROOM",
    "storey_range": "07 TO 09",
    "floor_area_sqm": 90,
    "flat_model": "Model A",
    "remaining_lease": 80
  }'
```

### Example 3: BTO Town Recommendations

```bash
curl "http://localhost:5000/bto/town_reco?type=highest&duration=3&limit=5"
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

For questions or support, please open an issue in the GitHub repository.