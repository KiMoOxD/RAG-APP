from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings 
from controllers import DataController, ProcessController
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from models.enums.AssetTypeEnum import AssetTypeEnum
from models import ResponseSignal

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)


@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    """Upload a file to Supabase Storage"""
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create(
        project_id=project_id
    )
    
    # Validate the file properties
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_file_properties(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Signal": result_signal}
        )
    
    # Generate unique file ID and storage path
    storage_path, file_id = data_controller.generate_unique_file_id(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to Supabase Storage
        upload_result = request.app.supabase_provider.upload_file(
            file_path=storage_path,
            file_content=file_content,
            content_type=file.content_type
        )
        
        if not upload_result.get("success"):
            logger.error(f"Error uploading file to Supabase: {upload_result.get('error')}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"Signal": ResponseSignal.FILE_UPLOAD_FAILED.value}
            )

    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Signal": ResponseSignal.FILE_UPLOAD_FAILED.value}
        )

    # Store the asset metadata in the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )
    
    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=len(file_content),
        asset_storage_path=storage_path
    )
    
    asset_record = await asset_model.create_asset(asset=asset_resource)
    
    return JSONResponse(
        content={
            "Signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "FileId": str(asset_record.id),
            "FileName": file_id,
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    """Process uploaded files into chunks"""
    chunk_size = process_request.chunk_size
    overlap = process_request.overlap
    do_reset = process_request.do_reset
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create(
        project_id=project_id
    )
    
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )
    
    project_files = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )
        
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "Signal": ResponseSignal.FILE_ID_ERROR.value,
                }
            )
            
        project_files = {
            asset_record.id: asset_record
        }
        
    else:
        assets = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value
        )
        
        project_files = {
            record.id: record
            for record in assets
        }
        
    if len(project_files) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "Signal": ResponseSignal.NO_FILES_ERROR.value,
            }
        )
    
    process_controller = ProcessController(project_id=project_id)

    no_records = 0 
    no_files = 0 
    
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )
    
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )
        
    for asset_id, asset in project_files.items():
        # Download file from Supabase Storage
        file_bytes = request.app.supabase_provider.download_file(
            file_path=asset.asset_storage_path
        )
        
        if file_bytes is None:
            logger.error(f"Error downloading file: {asset.asset_name}")
            continue
        
        # Process file content from bytes
        file_content = process_controller.get_file_content_from_bytes(
            file_bytes=file_bytes,
            file_id=asset.asset_name
        )
        
        if file_content is None:
            logger.error(f"Error processing file: {asset.asset_name}")
            continue
        
        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=asset.asset_name,
            chunk_size=chunk_size,
            overlap_size=overlap
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "Signal": ResponseSignal.PROCESSING_FAILED.value
                }
            )
        
        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]
        
        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1
        
    return JSONResponse(
        content={
            "Signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files
        }
    )