import datetime
import random


RETRYABLE = ["Missing modifier", "Incorrect NPI", "Prior auth required"]
NON_RETRYABLE = ["Authorization expired", "Incorrect provider type"]
AMBIGUOUS_MAPPING = {
    "incorrect procedure": "Please review procedure code",
    "form incomplete": "Please complete missing form fields",
    "not billable": "Check billable status with insurer",
    None: "Reason not provided"
}


def mock_llm_classifier(reason):
    """Pretend to call an LLM for ambiguous reasons."""
    mapping = {
        "incorrect procedure": "Please review procedure code",
        "form incomplete": "Please complete missing form fields",
        "not billable": "Check billable status with insurer",
        None: "Reason not provided"
    }
    return mapping.get(reason, "Ambiguous reason, manual review required")


def is_resubmittable(record, today):
    """Check if claim meets eligibility rules."""
    try:
        if record["status"] != "denied":
            return False, None, None

        if not record["patient_id"]:
            return False, None, None

        submitted_date = datetime.date.fromisoformat(record["submitted_at"])
        if (today - submitted_date).days <= 7:
            return False, None, None

        denial_reason = record.get("denial_reason")

        if denial_reason in RETRYABLE:
            return True, denial_reason, f"Review {denial_reason} and resubmit"

        if denial_reason in NON_RETRYABLE:
            return False, denial_reason, None

        # Handle ambiguous via mock classifier (mapping)
        if denial_reason in AMBIGUOUS_MAPPING:
            return True, denial_reason, AMBIGUOUS_MAPPING[denial_reason]

        if (denial_reason not in 
                RETRYABLE and denial_reason not in
                NON_RETRYABLE):
            suggestion = mock_llm_classifier(denial_reason)
            return True, denial_reason, suggestion

        return False, denial_reason, None
    except Exception as e:
        return False, f"error: {str(e)}", None
