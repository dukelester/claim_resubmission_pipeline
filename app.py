import os
import json

from fastapi import FastAPI, UploadFile, File

from pipeline.pipeline import ClaimResubmissionPipeline

app = FastAPI(title="Claim Resubmission API")


@app.post('/process')
async def process_files(alpha: UploadFile = File(None),
                        beta: UploadFile = File(None)):
    # Save uploaded files temporarily for processing
    if alpha:
        alpha_file_path = f"temp_{alpha.filename}"
        with open(alpha_file_path, "wb") as alpha_file:
            alpha_file.write(await alpha.read())
    else:
        alpha_file_path = "data/emr_alpha.csv"

    if beta:
        beta_file_path = f"temp_{beta.filename}"
        with open(beta_file_path, "wb") as beta_file:
            beta_file.write(await beta.read())
    else:
        beta_file_path = "data/emr_beta.json"

    pipeline = ClaimResubmissionPipeline(alpha_file_path, beta_file_path)
    summary = pipeline.run()
    return {
        "pipeline_summary": summary,
        "resubmission_candidates": pipeline.resubmission_candidates
    }


@app.get("/summary")
async def get_summary():
    """Return the latest saved pipeline summary and candidates."""
    summary = {}
    candidates = []

    if os.path.exists("resubmission_candidates.json"):
        with open("resubmission_candidates.json", "r") as f:
            candidates = json.load(f)

    if os.path.exists("rejected_records.json"):
        with open("rejected_records.json", "r") as f:
            rejected = json.load(f)
        summary["rejected_records_count"] = len(rejected)

    summary["resubmission_candidates_count"] = len(candidates)
    summary["resubmission_candidates"] = candidates

    return summary