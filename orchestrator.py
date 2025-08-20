from prefect import flow, task
from prefect.logging import get_run_logger

from pipeline.pipeline import ClaimResubmissionPipeline


@task
def load_and_process():
    """
    Prefect task to initialize and run the claim resubmission pipeline.

    Returns:
        dict: Summary statistics of the pipeline run including counts of
            eligible and excluded claims.
    """
    logger = get_run_logger()
    logger.info("INFO running the Pipeline")

    pipeline = ClaimResubmissionPipeline()
    return pipeline.run()


@task
def save_results(pipeline: ClaimResubmissionPipeline):
    """
    Prefect task to save the results of the pipeline execution.

    Args:
        pipeline (ClaimResubmissionPipeline): The pipeline instance containing
                                            processed results to be saved.
    """
    pipeline.save_results()


@flow
def claims_pipeline_flow():
    """
    Prefect flow to orchestrate the end-to-end claim resubmission pipeline.

    Steps:
        1. Initialize the pipeline.
        2. Run the pipeline to process Alpha and Beta claim records.
        3. Save eligible and rejected claim results to JSON files.
        4. Print a summary of the pipeline run.

    Returns:
        None
    """
    pipeline = ClaimResubmissionPipeline()
    summary = pipeline.run()
    pipeline.save_results()
    print(f"The Pipeline summary: {summary}")


if __name__ == "__main__":
    claims_pipeline_flow()
