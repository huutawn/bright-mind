import io
import asyncio
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter, Depends
from minio import Minio
from app.helpers.bases import DataResponse
from .services import upload_single, upload_multiple_files_to_minio
from app.core.config import settings
from app.helpers.deps import get_current_user
from app.core.minio_config import get_minio_client

router = APIRouter()


@router.post('/single', response_model=DataResponse[str])
async def handle_upload_single(file: UploadFile = File(...),
                               client: Minio = Depends(get_minio_client),
                               user=Depends(get_current_user)):
    file_url = await upload_single(minio_client=client,
                                   bucket_name=settings.MINIO_BUCKET,
                                   endpoint_url=settings.MINIO_ENDPOINT,
                                   file=file)
    return DataResponse(data=file_url)


@router.post("/multi", response_model=DataResponse[List[str]])
async def handle_upload_multiple_files(
        files: List[UploadFile] = File(...),
        client: Minio = Depends(get_minio_client),
        user = Depends(get_current_user)
):
    file_urls = await upload_multiple_files_to_minio(client, settings.MINIO_BUCKET, files)
    return DataResponse(data=file_urls)
