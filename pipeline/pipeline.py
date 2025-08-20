import json
import datetime
import logging

import pandas as pd


from .schema import normalize_alpha_records, normalize_beta_records
from .eligibility import is_resubmittable


TODAY = datetime.date(2025, 7, 30)


class ClaimResubmissionPipeline:
    """
    A pipeline to process medical claims from multiple EMR sources
    (Alpha CSV and Beta JSON).

    The pipeline loads records, normalizes them, determines resubmission
    eligibility, tracks exclusion reasons, and saves results for
    downstream review.
    """

    def __init__(
        self,
        alpha_file_path="data/emr_alpha.csv",
        beta_file_path="data/emr_beta.json"
            ):
        """
        Initialize the ClaimResubmissionPipeline with paths to data sources.
        """
        self.alpha_file_path = alpha_file_path
        self.beta_file_path = beta_file_path
        self.resubmission_candidates = []
        self.rejected_records = []
        self.exclusion_reasons = {}

    def load_alpha_records(self):
        """
        Load and normalize claims from the EMR Alpha CSV file.

        Returns:
            list[dict]: A list of normalized claim records from EMR Alpha.
        """
        df = pd.read_csv(self.alpha_file_path)
        return [normalize_alpha_records(record) for
                record in df.to_dict(orient="records")]

    def load_beta_records(self):
        """
        Load and normalize claims from the EMR Beta JSON file.

        Returns:
            list[dict]: A list of normalized claim records from EMR Beta.
        """
        with open(self.beta_file_path, "r", encoding="utf-8") as f:
            records = json.load(f)
        return [normalize_beta_records(record) for record in records]

    def run(self, today=TODAY):
        """
        Execute the claim processing pipeline.

        Args:
            today (datetime.date): Reference date for determining resubmission
            eligibility.

        Returns:
            dict: Summary of pipeline results including counts and breakdown.
                Example:
                {
                    "total_claims": 120,
                    "from_alpha": 70,
                    "from_beta": 50,
                    "eligible_for_resubmission": 45,
                    "excluded": 75,
                    "excluded_breakdown": {"Expired": 30, "Missing fields": 45}
                }
        """
        alpha_records = self.load_alpha_records()
        beta_records = self.load_beta_records()
        all_records = alpha_records + beta_records

        logging.info("Claim Records From alpha:  %s", alpha_records)
        logging.info("Claim Records From Beta:  %s", beta_records)
        logging.info("Total loaded claims: %s", len(all_records))

        for record in all_records:
            eligible, reason, recommendation = is_resubmittable(record, today)
            if eligible:
                self.resubmission_candidates.append({
                    "claim_id": record["claim_id"],
                    "resubmission_reason": reason,
                    "source_system": record["source_system"],
                    "recommended_changes": recommendation
                })
            else:
                self.rejected_records.append(record)
                reason_key = reason or "Unknown reason"
                self.exclusion_reasons[reason_key] = (
                    self.exclusion_reasons.get(reason_key, 0) + 1)

        return {
            "total_claims": len(all_records),
            "from_alpha": len(alpha_records),
            "from_beta": len(beta_records),
            "eligible_for_resubmission": len(self.resubmission_candidates),
            "excluded": len(self.rejected_records),
            "excluded_breakdown": self.exclusion_reasons
        }

    def save_results(self):
        """
        Save resubmission candidates and rejected records into JSON files.

        Creates:
            - resubmission_candidates.json
            - rejected_records.json

        Logs:
            Info message upon successful save.
        """
        with open("resubmission_candidates.json", "w", encoding="utf-8") as f:
            json.dump(self.resubmission_candidates, f, indent=2)

        with open("rejected_records.json", "w", encoding="utf-8") as f:
            json.dump(self.rejected_records, f, indent=2)

        logging.info("Results saved successfully.")
