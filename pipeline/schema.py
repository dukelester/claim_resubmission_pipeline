import datetime


def normalize_alpha_records(record):
    """Normalize CSV record to a unified schema.
    """
    return {
        "claim_id": record.get("claim_id"),
        "patient_id": record.get("patient_id") or None,
        "procedure_code": record.get("procedure_code"),
        "denial_reason": record.get("denial_reason") or None,
        "status": record.get("status").lower(),
        "submitted_at": str(
            datetime.date.fromisoformat(record["submitted_at"])),
        "source_system": "alpha"
    }


def normalize_beta_records(record):
    """Normalize JSON record to unified schema."""
    return {
        "claim_id": record.get("id"),
        "patient_id": record.get("member") or None,
        "procedure_code": record.get("code"),
        "denial_reason": record.get("error_msg") or None,
        "status": record.get("status").lower(),
        "submitted_at": str(
            datetime.date.fromisoformat(record["date"].split("T")[0])),
        "source_system": "beta"
    }
