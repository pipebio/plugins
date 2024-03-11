import os
import traceback

from pipebio.models.job_status import JobStatus
from pipebio.pipebio_client import PipebioClient

from custom_code import trinityJob

if __name__ == '__main__':
    client = PipebioClient()

    try:
        client.jobs.update(status=JobStatus.RUNNING,
                           progress=10,
                           messages=['Running plugin job.'])

        user = client.user
        job = client.jobs.get()

        client.jobs.update(status=JobStatus.RUNNING,
                           progress=20,
                           messages=[f"Logged in for {user['firstName']} {user['lastName']}."])

        input_entity_ids = os.environ["INPUT_ENTITIES"] if "INPUT_ENTITIES" in os.environ else ""
        input_entity_ids = list(
            map(
                lambda input_entity_id: input_entity_id.strip(), input_entity_ids.split(",")
            )
        )

        if len(input_entity_ids) == 0:
            raise Exception("INPUT_ENTITIES missing")

        folder_key = 'TARGET_FOLDER_ID'
        target_folder_id = os.environ[folder_key] if folder_key in os.environ else None

        output_entity_id = trinityJob.run(client, user, input_entity_ids, target_folder_id)

        client.jobs.set_complete(messages=["Completed plugin job."],
                                 output_entity_ids=[output_entity_id])

    except Exception as exception:
        print("Runner caught exception")
        track = traceback.format_exc()
        str_exception = str(exception)
        print(str_exception)
        print(track)
        client.jobs.update(status=JobStatus.FAILED,
                           progress=100,
                           messages=[f"Unexpected error in plugin job: {str_exception}"])
        raise exception
