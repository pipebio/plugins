import os

from pipebio.models.job_type import JobType
from pipebio.pipebio_client import PipebioClient

from runner import main

if __name__ == '__main__':
    client = PipebioClient()

    # The project where the input files are and where then output file/s will be written.
    # Add the project id here.
    shareable_id = '<ADD_PROJECT_ID_HERE>'

    # Ids of the documents, used as inputs for the plugin.
    # Add your input doc ids here.
    input_entity_ids = []

    # Create a new job
    job_id = client.jobs.create(shareable_id=shareable_id,
                                job_type=JobType.PluginJob,
                                input_entity_ids=input_entity_ids,
                                name='Example run test',
                                # Important client_side is set, it creates a record for the job, to be used
                                # by your plugin code, but does not actually run anything, that is done in the
                                # `docker run....` step.
                                client_side=True)

    # Set the job_id as env var, so it can be used in the plugin - this is handled by PipeBio infrastructure when
    # running your plugin, however as we are running locally, we need to do this manually.
    os.environ['JOB_ID'] = job_id

    # Execute the runner code.
    main()
