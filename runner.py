import os

from pipebio.models.job_status import JobStatus
from pipebio.pipebio_client import PipebioClient

from custom_code import downloader

if __name__ == '__main__':
    client = PipebioClient()

    client.jobs.update(JobStatus.RUNNING, 25, ['Running custom job.'])

    user = client.user
    print(f"Using api key for {user['firstName']} {user['lastName']}.")

    client.jobs.update(JobStatus.RUNNING, 50, [f"Logged in for {user['firstName']} {user['lastName']}."])

    input_entity_ids = os.environ["INPUT_ENTITIES"] if "INPUT_ENTITIES" in os.environ else ""
    input_entity_ids = input_entity_ids.split(",")

    if len(input_entity_ids) == 0:
        raise Exception('INPUT_ENTITIES missing')

    downloader.download_files(client, input_entity_ids)

    client.jobs.set_complete(['Completed custom job.'])
