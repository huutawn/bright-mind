import io
from fastapi import UploadFile, HTTPException
from minio import Minio
from minio.error import S3Error
from typing import List
import asyncio
import logging
from app.core.config import settings


async def upload_single(minio_client: Minio,
                        bucket_name: str,
                        endpoint_url: str,
                        file: UploadFile) -> str:
    try:
        contents = await file.read()
        file_size = len(contents)
        object_name = file.filename

        res = minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=io.BytesIO(contents),
            length=file_size,
            content_type=file.content_type
        )
        scheme = "http://" if not endpoint_url.startswith("http") else ""
        file_url = f"{scheme}{endpoint_url}/{bucket_name}/{object_name}"
        return file_url
    except S3Error as exc:
        raise HTTPException(status_code=500, detail=str(exc))


async def upload_multiple_files_to_minio(client: Minio, bucket: str, files: List[UploadFile]) -> List[str]:
    async def _upload_task(file: UploadFile):
        return await upload_single(client, bucket, settings.MINIO_ENDPOINT, file)

    tasks = [_upload_task(file) for file in files]
    uploaded_urls = await asyncio.gather(*tasks)
    return uploaded_urls
