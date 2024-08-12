import os
import traceback

from pipebio.models.job_status import JobStatus
from pipebio.pipebio_client import PipebioClient

from custom_code import trinityJob
from exceptions import UserFacingException

if __name__ == '__main__':
    client = PipebioClient()

    try:
        # Update the job, to indicate that it is running.
        client.jobs.update(status=JobStatus.RUNNING,
                           progress=1,
                           messages=['Running plugin job.'])

        user = client.user
        job = client.jobs.get()

        client.jobs.update(status=JobStatus.RUNNING,
                           progress=20,
                           messages=[f"Logged in for {user['firstName']} {user['lastName']}."])

        # Get the input_entity_ids from the job inputEntities.
        input_entities = job['inputEntities'] if job['inputEntities'] is not None else []
        input_entity_ids = list(
            map(
                lambda input_entity: input_entity['id'], input_entities
            )
        )

        if len(input_entity_ids) == 0:
            raise Exception("No documents found in inputEntities")

        folder_key = 'TARGET_FOLDER_ID'
        target_folder_id = int(os.environ[folder_key]) if folder_key in os.environ else None

        # This is the line a plugin author would change, to call your custom code.
        # Below are passed as args (though your use case may need different args):
        #     - the PipeBio client instance.
        #     - the ids of the entities to process (parsed from the job inputs).
        #     - the id of the folder to write the job results to (parsed from the job inputs).
        output_entity = trinityJob.run(client, input_entity_ids, target_folder_id)

        # Set job as complete, adding the entity id of the output, so it is shown in the jobs table.
        output_entity_id = output_entity['id']
        client.jobs.set_complete(messages=["Completed plugin job."],
                                 output_entity_ids=[output_entity_id])

    except UserFacingException as exception:
        track = traceback.format_exc()
        print('job_wrapper: caught SafeException!!!')
        print(str(exception))
        print(track)
        client.jobs.update(status=JobStatus.FAILED,
                           progress=100,
                           messages=[exception.user_message])


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
