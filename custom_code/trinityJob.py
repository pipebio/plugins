import os
import subprocess
import time
from typing import List

from pipebio.column import Column
from pipebio.models.job_status import JobStatus
from pipebio.models.table_column_type import TableColumnType
from pipebio.pipebio_client import PipebioClient
from pipebio.util import Util


def get_file(client, entity_id: str, destination_location: str = None) -> str:
    # Set the download name and folder.
    r = client.entities.get(entity_id)
    print(r)
    destination_filename = f"{entity_id}.tsv"
    destination_location = Util.get_executed_file_location() if destination_location is None else destination_location
    absolute_location = os.path.join(destination_location, destination_filename)

    client.sequences.download(entity_id, destination=absolute_location)
    columns = [
        Column('id', TableColumnType.STRING),
        Column('name', TableColumnType.STRING),
        Column('description', TableColumnType.STRING),
        Column('sequence', TableColumnType.STRING),
        Column('quality', TableColumnType.STRING),
    ]
    sequence_map = {}
    client.sequences.read_tsv_to_map(filepath=absolute_location,
                                     columns=columns,
                                     id_prefix=entity_id,
                                     sequence_map=sequence_map)

    filename = f"/tmp/{entity_id}.fq"
    with open(filename, mode="w") as file:
        for key, row in sequence_map.items():
            compound_id = f"{row['name']} {row['description']}"
            line = f"@{compound_id}\n{row['sequence']}\n+\n{row['quality']}\n"
            file.writelines([line])

    return filename


def run_trinity(files: List[str]) -> str:
    output_file = "/tmp/trinity_output"
    command = f"/root/trinityrnaseq-v2.15.1/Trinity" \
              f" --seqType fq --left {files[0]} " \
              f"--right {files[1]} " \
              f"--output {output_file} --max_memory 2G"

    print(f"Running: {command}")
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print(line)
    p.wait()

    return f"{output_file}.Trinity.fasta"


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


def run(client: PipebioClient, user, entity_ids: List[str], target_folder_id: str):
    if len(entity_ids) != 2:
        raise Exception("Trinity job supports two inputs only")

    files = []
    for entity_id in entity_ids:
        files.append(get_file(client, entity_id, "/tmp"))

    client.jobs.update(JobStatus.RUNNING, 40, ["Downloaded files."])

    file_1 = client.entities.get(entity_ids[0])
    file_2 = client.entities.get(entity_ids[1])
    owner_id = file_1['ownerId']
    file_name = f"Trinity output ({file_1['name']} & {file_2['name']})"

    output_file = run_trinity(files)
    print(output_file)

    client.jobs.update(JobStatus.RUNNING, 60, ["Ran trinity tool."])

    organisation_id = user['orgs'][0]['id']
    import_job = client.upload_file(file_name=file_name,
                                    absolute_file_location=output_file,
                                    organization_id=organisation_id,
                                    parent_id=int(target_folder_id),
                                    project_id=owner_id)

    finished_job = wait_for_job_to_finish(client, import_job["id"])

    client.jobs.update(JobStatus.RUNNING, 80, ["Uploaded output file."])

    return finished_job["outputEntities"][0]["id"]
