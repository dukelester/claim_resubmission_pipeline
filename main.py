import json
import logging

from pipeline.pipeline import ClaimResubmissionPipeline

# Pipeline Logging
logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# The Log summary

# logging.info("Eligible claims : %s", len(resubmission_candidates))
# logging.info("Rejected claims : %s", len(rejected_records))
# logging.info("Exclusion reason Breakdown Summary: %s", exclusion_reasons)


if __name__ == "__main__":
    pipeline = ClaimResubmissionPipeline()
    summary = pipeline.run()
    pipeline.save_results()
    print(json.dumps(summary, indent=2))
    logging.info("Pipeline Summary: %s ", json.dumps(summary, indent=2))
