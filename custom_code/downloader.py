from typing import List

from pipebio.pipebio_client import PipebioClient


def download_file(client: PipebioClient, entity_id: int):
    print(f"Downloading entity_id: {entity_id}")

    entity = client.sequences.download_to_memory([entity_id])

    keys = list(entity.keys())

    print("\nListing sequence ids and names:\n")

    for key in keys:
        row = entity[key]
        print(f"{row['id']}: {row['name']}")


def download_files(client: PipebioClient, entity_ids: List[str]):
    for entity_id in entity_ids:
        download_file(client, int(entity_id))
