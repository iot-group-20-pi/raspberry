from __future__ import annotations

import os
from multiprocessing import Process, Queue

import cv2
from numpy.typing import NDArray

from utils.config import env

# Tuple of (datetime ISO, result JSON|None, original image NDArray|None)
FILE_DATA = tuple[str, str | None, NDArray | None]


def file_thread(in_q: Queue[FILE_DATA], upload=False):
    from pathlib import Path

    uploader_q: Queue[str] | None = None
    if upload:
        uploader_q = Queue()
        uploader_process = Process(target=_uploader_thread, args=(uploader_q,))
        uploader_process.start()

    while True:
        iso_datetime, result_json, original_img = in_q.get()

        date_folder = os.path.join(env["DATA_FOLDER"], iso_datetime.split("T")[0])
        Path(date_folder).mkdir(parents=True, exist_ok=True)

        if result_json is not None:
            filepath = os.path.join(date_folder, f"{iso_datetime}.json")
            with open(filepath, "w") as file:
                file.write(result_json)

            if uploader_q is not None:
                uploader_q.put(filepath)

        if original_img is not None:
            filepath = os.path.join(date_folder, f"{iso_datetime}-raw.jpg")
            cv2.imwrite(filepath, original_img)

            if uploader_q is not None:
                uploader_q.put(filepath)


def _uploader_thread(in_q: Queue[str]):
    import boto3
    # from boto3.s3.transfer import S3UploadFailedError

    s3_client = boto3.client(
        "s3",
        region_name=env["AWS"]["REGION_NAME"],
        aws_access_key_id=env["AWS"]["ACCESS_KEY_ID"],
        aws_secret_access_key=env["AWS"]["SECRET_ACCESS_KEY"],
    )

    while True:
        filepath = in_q.get()
        filename = os.path.basename(filepath)

        with open(filepath, "rb") as file:
            s3_client.put_object(Bucket=env["BUCKET_NAME"], Key=filename, Body=file)

        # except S3UploadFailedError as err:
        #     print(f"Couldn't upload file {filename} to {bucket.name}.")
        #     print(f"\t{err}")
