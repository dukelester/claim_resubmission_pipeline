# Claim Resubmission Ingestion Pipeline

This project implements **Case Study 1** from the Humaein AI Full Stack Developer screening challenge.  
It is a data engineering pipeline that ingests healthcare claim data from multiple EMR systems, normalizes the schema, and applies business rules to identify claims eligible for **automated resubmission**.

---

## 📌 Features
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
├── data/
│   ├── emr_alpha.csv        # Sample CSV source
│   ├── emr_beta.json        # Sample JSON source
├── pipeline/
│   ├── __init__.py
│   ├── schema.py            # Schema normalization helpers
│   ├── eligibility.py       # Eligibility rules
│   ├── pipeline.py          # (optional orchestration helpers)
├── logs/
│   └── pipeline.log         # Logs written after each run
├── resubmission_candidates.json   # Output (generated)
├── rejected_records.json          # Output (generated)
├── main.py                  # Entry point for pipeline
├── requirements.txt
└── README.md
└── .gitignore
```

## Setup & Installation

Clone the repository:

```git clone https://github.com/dukelester/claim_resubmission_pipeline.git

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