import json
import logging
import datetime
import pandas as pd


from pipeline.schema import normalize_alpha, normalize_beta
from pipeline.eligibility import is_resubmittable


# Pipeline Logging
logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


TODAY = datetime.date(2025, 7, 30)


def load_alpha_file(file_path: str):
    """ Load the CSV file for the alpha.csv from the source """
    df = pd.read_csv(file_path)
    records = df.to_dict(orient="records")
    return [normalize_alpha(record) for record in records]


def load_beta_file(file_path: str):
    """ Load the CSV file for the beta.json from the source """
    with open(file_path, "r", encoding="utf-8") as beta_file:
        records = json.load(beta_file)
        return [normalize_beta(record) for record in records]


def run_pipeline():
    alpha_records = load_alpha_file("data/emr_alpha.csv")
    beta_records = load_beta_file("data/emr_beta.json")

    from_alpha = len(alpha_records)
    from_beta = len(beta_records)

    logging.info("Claim Records From alpha:  %s", from_alpha)
    logging.info("Claim Records From Beta:  %s", from_beta)

    combined_records = alpha_records + beta_records
    logging.info("Total loaded claims: %s", len(combined_records))

    resubmission_candidates = []
    rejected_records = []
    exclusion_reasons = {}

    for record in combined_records:
        eligible, reason, recommendation = is_resubmittable(record, TODAY)
        if eligible:
            resubmission_candidates.append(
                {
                    "claim_id": record["claim_id"],
                    "resubmission_reason": reason,
                    "source_system": record["source_system"],
                    "recommended_changes": recommendation
                })
        else:
            rejected_records.append(record)
            reason_key = reason or "Unknown reason"
            exclusion_reasons[reason_key] = (
                exclusion_reasons.get(reason_key, 0) + 1)

    # Save the output to a file
    with open("resubmission_candidates.json", "w", encoding="utf-8") as f:
        json.dump(resubmission_candidates, f, indent=2)

    with open("rejected_records.json", "w", encoding="utf-8") as f:
        json.dump(rejected_records, f, indent=2)

    # The Log summary

    logging.info("Eligible claims : %s", len(resubmission_candidates))
    logging.info("Rejected claims : %s", len(rejected_records))
    logging.info("Exclusion reason Breakdown Summary: %s", exclusion_reasons)


if __name__ == "__main__":
    run_pipeline()
