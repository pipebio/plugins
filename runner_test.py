import os
import subprocess

from pipebio.models.job_type import JobType
from pipebio.pipebio_client import PipebioClient

# This file allows you to run a docker image locally, to test code as you write it.
# You will need to set:
# - shareable_id
# - input_entity_ids
# - docker_image

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
                                # Important this is set, it creates a record for the job, to be used
                                # by your plugin code, but does not actually run anything, that is done in the
                                # `docker run....` step.
                                client_side=True)

    # Set the image you wish to run, this can be a local image or one you have pushed to dockerhub.
    # Replace this with your image tag.
    docker_image = "pipebio/trinity-job:latest"

    # Set your PIPE_API_KEY in a .env file, it will be ready automatically by the Pipebio SDK and set as an env var
    # (see https://pypi.org/project/pipebio/ for details of using an .env file).
    #
    # This is not needed when running on Pipebio infrastructure, but as you are running a docker image
    # locally, its required to be able to authenticate.
    PIPE_API_KEY = os.environ['PIPE_API_KEY']

    commands = [
        f"docker run",
        f"-e JOB_ID={job_id}",
        f"-e NUMBER_OF_CPUS=1",
        f"-e PIPE_API_KEY={PIPE_API_KEY}",
        f"{docker_image}",
    ]

    command = " ".join(commands)

    print(f"Running: {command}")

    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in p.stdout.readlines():
        print(line)
    p.wait()
