# Claim Resubmission Ingestion Pipeline

This project implements **Case Study 1** from the Humaein AI Full Stack Developer screening challenge.  
It is a data engineering pipeline that ingests healthcare claim data from multiple EMR systems, normalizes the schema, and applies business rules to identify claims eligible for **automated resubmission**.

---

## Features
- Ingests **CSV** (Alpha source) and **JSON** (Beta source) claims data.
- Normalizes all records into a **unified schema**:
  ```json
  {
    "claim_id": "string",
    "patient_id": "string or null",
    "procedure_code": "string",
    "denial_reason": "string or null",
    "status": "approved/denied",
    "submitted_at": "ISO date",
    "source_system": "alpha or beta"
  }


### Applies eligibility rules for resubmission:

    - Claim status = denied

    - Patient ID is not null

    - Claim submitted more than 7 days ago (relative to 2025-07-30)

    - Denial reason is retryable (or mapped from ambiguous reasons)

### Outputs results into:

    - resubmission_candidates.json => eligible claims

    - rejected_records.json => invalid/non-retryable claims

#### Includes basic logging (pipeline metrics + errors).


## Project Structure

```claim_resubmission_pipeline/
├── app.py # FastAPI endpoint
├── orchestrator.py # Prefect flow simulation
├── data/
│ ├── emr_alpha.csv
│ ├── emr_beta.json
├── pipeline/
│ ├── init.py
│ ├── schema.py # Schema normalization
│ ├── eligibility.py # Eligibility logic + mock LLM
│ ├── pipeline.py # ClaimPipeline class
├── logs/
│ ├── pipeline.log
│ └── failed_records.log # Exported rejected records
├── resubmission_candidates.json
├── rejected_records.json
├── main.py
├── requirements.txt
└── README.md
└── .gitignore
```

## Setup & Installation

Clone the repository:

```
git clone https://github.com/dukelester/claim_resubmission_pipeline.git

cd claim_resubmission_pipeline
```


### Create and activate a virtual environment:

```python3 -m venv venv
source venv/bin/activate      # Mac/Linux
OR venv\Scripts\activate    # Windows
```


### Install dependencies:

`pip install -r requirements.txt`

## Running the Pipeline

`python main.py`

### This will:

    * Load data from data/emr_alpha.csv and data/emr_beta.json.

    * Normalize and process all records.

    * Save results into:

    resubmission_candidates.json

    rejected_records.json

    * Log execution summary into logs/pipeline.log.


## Bonus Features

### 1. Modular Pipeline Class

The core pipeline is encapsulated in `ClaimResubmissionPipeline`:

```
from pipeline.pipeline import ClaimResubmissionPipeline

pipeline = ClaimResubmissionPipeline()
summary = pipeline.run()
pipeline.save_results()
```

This makes it easy to reuse in scripts, tests, or APIs.

### 2. FastAPI Endpoint

Run:

`uvicorn app:app --reload`


Upload claim files and process them dynamically:

```
curl -X POST "http://127.0.0.1:8000/process" \
     -F "alpha=@data/emr_alpha.csv" \
     -F "beta=@data/emr_beta.json"

```
Response:

```
{
  "summary": { "total_claims": 9, "eligible_for_resubmission": 5, ... },
  "resubmission_candidates": [ ... ]
}

```
### 3. Prefect Orchestration Simulation

The project includes orchestrator.py with a Prefect-style flow:

`python orchestrator.py`


This demonstrates how the pipeline can be orchestrated in a production-grade workflow manager.

### 4. Mock LLM Classifier

For ambiguous denial reasons (e.g., "incorrect procedure"), the pipeline uses a mock LLM classifier to infer retryable actions:

```
"incorrect procedure" → "Please review procedure code"
"form incomplete" → "Please complete missing form fields"
"not billable" → "Check billable status with insurer"
```

### 5. Failed Records Export

Rejected claims are saved into:

rejected_records.json (structured format)

logs/failed_records.log (line-by-line JSON for auditing)