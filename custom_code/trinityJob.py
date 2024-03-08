import time
from typing import List

import requests
from pipebio.models.job_status import JobStatus
from pipebio.models.job_type import JobType
from pipebio.pipebio_client import PipebioClient


def wait_for_job_to_finish(client: PipebioClient, job_id: str):
    done = False
    job = None

    while not done:
        job = client.jobs.get(job_id)
        job_status = job['status']
        print(f'job status: {job_status}')
        done = job_status in [JobStatus.COMPLETE.value, JobStatus.FAILED.value]
        if not done:
            time.sleep(5)

    return job


def get_source_file(client: PipebioClient, user, entity_id: str, index: int) -> str:
    job_id = client.jobs.create(job_type=JobType.ExportJob,
                                input_entity_ids=[int(entity_id)],
                                owner_id=user["orgs"][0]["id"],
                                name="Export source files",
                                shareable_id="1c3a16dc-7316-42e1-b3aa-f3954e43f1bc",
                                params={
                                    "format": "ORIGINAL",
                                })
    job = wait_for_job_to_finish(client, job_id)

    url = job["outputLinks"][0]["url"]

    response = requests.get(url)
    if "content-disposition" in response.headers:
        content_disposition = response.headers["content-disposition"]
        disposition_filename = content_disposition.split('filename=')[1].strip('\"')
        filename = f"/tmp/{disposition_filename}"
    else:
        filename = f"/tmp/file_{index}"

    with open(filename, mode="wb") as file:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            file.write(chunk)
        print(f"Downloaded file {filename}")

    return filename


def run(client: PipebioClient, user, entity_ids: List[str]):
    files = []
    for i, entity_id in enumerate(entity_ids):
        files.append(get_source_file(client, user, entity_id, i))

    print(files)
