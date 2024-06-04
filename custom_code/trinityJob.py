import os
import subprocess
import time
from typing import List
import psutil
from Bio import SeqIO
from pipebio.column import Column, IntegerColumn, StringColumn
from pipebio.models.entity_types import EntityTypes
from pipebio.models.job_status import JobStatus
from pipebio.models.table_column_type import TableColumnType
from pipebio.pipebio_client import PipebioClient
from pipebio.uploader import Uploader
from pipebio.util import Util

from exceptions import UserFacingException


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
    available_cpu = get_number_of_cpus()

    commands = [
        f"/root/trinityrnaseq-v2.15.1/Trinity",
        f"--seqType fq",
        f"--left {files[0]} ",
        f"--right {files[1]} ",
        f"--CPU {available_cpu} ",
        f"--max_memory 40G ",
        f"--output {output_file} "
    ]

    command = " ".join(commands)

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


def run(client: PipebioClient, user, entity_ids: List[str], target_folder_id: str) -> dict:
    if len(entity_ids) != 2:
        raise Exception("Trinity job supports two inputs only")

    client.jobs.update(JobStatus.RUNNING, 10, ["Downloading input documents"])

    files = list(get_file(client, entity_id, "/tmp") for entity_id in entity_ids)

    client.jobs.update(JobStatus.RUNNING, 20, ["Downloaded input documents"])

    file_1 = client.entities.get(entity_ids[0])
    file_2 = client.entities.get(entity_ids[1])
    project_id = file_1['ownerId']
    file_name = f"Trinity output ({file_1['name']} & {file_2['name']})"

    client.jobs.update(JobStatus.RUNNING, 30, ["Running trinity"])

    output_file = run_trinity(files)

    if not os.path.exists(output_file):
        raise UserFacingException("Trinity failed to create a result.")

    print(f'Created trinity output: {output_file}')

    client.jobs.update(JobStatus.RUNNING, 70, ["Ran trinity"])

    organization_id = user['orgs'][0]['id']

    result = client.entities.create_file(
        project_id=project_id,
        parent_id=int(target_folder_id),
        name=file_name,
        entity_type=EntityTypes.SEQUENCE_DOCUMENT,
        visible=False
    )

    schema = [IntegerColumn('id'), StringColumn('name'), StringColumn('sequence')]
    uploader = Uploader(
        result['id'],
        schema,
        client.sequences,
        chunk_size=100 * 1000 * 1000,
        make_charts=False,
        entity_type=EntityTypes.SEQUENCE_DOCUMENT
    )
    with open(output_file) as trinity_result:
        for record in SeqIO.parse(trinity_result, "fasta"):
            uploader.write_data({
                'name': record.name,
                'sequence': record.seq,
            })

    uploader.upload(allow_empty=False)

    return result


def get_number_of_cpus() -> int:
    """
    Returns the number of available CPUS using the best information available.

    In docker containers it's difficult to get the number of CPUS which can be dangerous:
      - if underestimated we don't make use of the available resource and jobs run too slow
      - if overestimated the job will run (much) slower because it tries to run too many processes

    Therefore we prefer to use explicit environment variables wherever possible and fallback to psutil which is
    more convenient for running unit tests / development etc.
    """
    count = int(os.environ['NUMBER_OF_CPUS']) if 'NUMBER_OF_CPUS' in os.environ else psutil.cpu_count(logical=False)

    print('number_of_cpus={}'.format(count))

    return 1
