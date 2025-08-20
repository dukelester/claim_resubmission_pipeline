from fastapi import FastAPI, UploadFile, File
import pandas as pd
import json
from pipeline.pipeline import ClaimResubmissionPipeline

app = FastAPI(title="Claim Resubmission API")


@app.post('/process')
async def process_files(alpha: UploadFile = File(None),
                        beta: UploadFile = File(None)):
    # Save uploaded files temporarily for processing
    if alpha:
        alpha_file_path = f"temp_{alpha.filename}"
        with open(alpha_file_path, "wb", encoding="utf-8") as alpha_file:
            alpha_file.write(await alpha_file.read())
    else:
        alpha_file_path = "data/emr_alpha.csv"

    if beta:
        beta_file_path = f"temp_{beta.filename}"
        with open(beta_file_path, "wb", encoding="utf-8") as beta_file:
            beta_file.write(await beta_file.read())
    else:
        beta_file_path = "data/emr_beta.json"

    pipeline = ClaimResubmissionPipeline(alpha_file_path, beta_file_path)
    summary = pipeline.run()
    return {
        "pipeline_summary": summary,
        "resubmission_candidates": pipeline.resubmission_candidates
    }
