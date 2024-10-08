import os
import traceback
from typing import Optional

from pipebio.models.job_status import JobStatus
from pipebio.pipebio_client import PipebioClient

from custom_code import trinityJob
from exceptions import UserFacingException


def main():
    """
    This is the entrypoint of the plugin.
    Plugin authors should only edit the line that calls their custom code,
    the rest can be seen as boilerplate that sets up the plugin.
    :return:
    """
    client = PipebioClient()

    try:
        job = client.jobs.get()
        user = client.user

        # Update the job, to indicate that it is running.
        client.jobs.update(status=JobStatus.RUNNING,
                           progress=1,
                           messages=['Running plugin job.'])

        # Add job status message, showing the user the plugin is running as.
        client.jobs.update(status=JobStatus.RUNNING,
                           progress=10,
                           messages=[f"Logged in for {user['firstName']} {user['lastName']}."])

        # Get the input_entity_ids from the job inputEntities.
        input_entities = job['inputEntities'] if job['inputEntities'] is not None else []
        input_entity_ids = list(
            map(
                lambda input_entity: input_entity['id'], input_entities
            )
        )

        # Sanity check, to ensure there is at least one input document.
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
        print("job_wrapper: caught SafeException!!!")
        print(str(exception))
        print(track)
        messages = [exception.user_message]

        creator = get_plugin_author(client, job)
        if creator is not None:
            # Allows users who experience issue to get in contact with the Plugin creator.
            messages.append(f"The plugin developer {creator} may be able to help")

        client.jobs.update(status=JobStatus.FAILED,
                           progress=100,
                           messages=messages)

    except Exception as exception:
        print("Runner caught exception")
        track = traceback.format_exc()
        str_exception = str(exception)
        print(str_exception)
        print(track)
        messages = [f"Unexpected error in plugin job: {str_exception}"]

        creator = get_plugin_author(client, job)
        if creator is not None:
            # Allows users who experience issue to get in contact with the Plugin creator.
            messages.append(f"The plugin developer {creator} may be able to help")

        client.jobs.update(status=JobStatus.FAILED,
                           progress=100,
                           messages=messages)
        raise exception


def get_plugin_author(client, job) -> Optional[str]:
    """
    Utility function to look up the creator of a plugin, useful for creating helpful error messages for users.
    :param client:
    :param job:
    :return:
    """
    plugin_id = job["params"]["pluginId"] if "params" in job and "pluginId" in job["params"] else None
    organization_id = client.user["orgs"][0]["id"] if "orgs" in client.user and len(client.user["orgs"]) > 0 and "id" in client.user["orgs"][0] else None

    if plugin_id is None or organization_id is None:
        return None

    plugin_response = client.session.get(f"organizations/{organization_id}/lists/{plugin_id}")
    plugin_response_json = plugin_response.json()
    creator_id = plugin_response_json["creatorId"] if "creatorId" in plugin_response_json else None

    if creator_id is None:
        return None

    user_response = client.session.get(f"organizations/{organization_id}/users/{creator_id}")
    user = user_response.json()

    return user["email"] if "email" in user else None


if __name__ == '__main__':
    main()
