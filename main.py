from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException, Query
from typing import List, Optional
import aiomysql
from database import get_db_conn
from fastapi import File, UploadFile
from azure.storage.blob import BlobServiceClient
from config import settings
from fastapi import HTTPException
from models.Project import Project
from models.User import User
from repositories.ProjectRepository import ProjectRepository
from repositories.UserRepository import UserRepository 

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test-db")
async def test_db(db: aiomysql.Cursor = Depends(get_db_conn)):
    try:
        await db.execute("SELECT DATABASE();")
        result = await db.fetchone()
        return {
            "status": "success",
            "message": f"Connected to database: {result['DATABASE()']}",
            "database": result['DATABASE()']
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error connecting to the database: {str(e)}"
        }
    



@app.post("/create-user")
async def create_user(name: str, db: aiomysql.Cursor = Depends(get_db_conn)):
    try:
        user_repo = UserRepository(db)
        user = User(name=name)
        user_id = await user_repo.create(user)
        return {
            "status": "success",
            "message": "User created successfully",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")



@app.post("/create-project")
async def create_project(
    name: str = Form(...),
    user_id: int = Form(...),
    description: Optional[str] = Form(None),
    documents: List[UploadFile] = File(None),
    photos: List[UploadFile] = File(None), 
    links: List[str] = Form(None),
    db_conn: aiomysql.Connection = Depends(get_db_conn)
):
    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
    container_client = blob_service_client.get_container_client(settings.azure_storage_container_name)
    
    # Upload documents and photos, and store their paths
    document_paths = []
    photo_paths = []
    
    if documents:
        for doc in documents:
            blob_client = container_client.get_blob_client(f"documents/{doc.filename}")
            content = await doc.read()
            blob_client.upload_blob(content, overwrite=True)
            document_paths.append(blob_client.url)
    
    if photos:
        for photo in photos:
            blob_client = container_client.get_blob_client(f"photos/{photo.filename}")
            content = await photo.read()
            blob_client.upload_blob(content, overwrite=True)
            photo_paths.append(blob_client.url)
    
    # Create project with file paths
    project = Project(
        name=name,
        user_id=user_id,
        description=description,
        documents=document_paths,
        photos=photo_paths,
        links=links
    )
    
    project_repo = ProjectRepository(db_conn)
    project_id = await project_repo.create(project)
    
    return {
        "status": "success",
        "message": "Project created successfully",
        "project_id": project_id
    }

@app.put("/update-project/{project_id}")
async def update_project(
    project_id: int,
    name: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    documents: Optional[List[UploadFile]] = File(None),
    photos: Optional[List[UploadFile]] = File(None),
    links: Optional[List[str]] = Form(None),
    db_conn: aiomysql.Connection = Depends(get_db_conn)
):
    project_repo = ProjectRepository(db_conn)
    existing_project = await project_repo.get_by_id(project_id)
    
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
    container_client = blob_service_client.get_container_client(settings.azure_storage_container_name)
    
    # Update documents and photos if provided
    if documents:
        document_paths = []
        for doc in documents:
            blob_client = container_client.get_blob_client(f"documents/{doc.filename}")
            content = await doc.read()
            blob_client.upload_blob(content, overwrite=True)
            document_paths.append(blob_client.url)
        existing_project.documents = document_paths
    
    if photos:
        photo_paths = []
        for photo in photos:
            blob_client = container_client.get_blob_client(f"photos/{photo.filename}")
            content = await photo.read()
            blob_client.upload_blob(content, overwrite=True)
            photo_paths.append(blob_client.url)
        existing_project.photos = photo_paths
    
    # Update other fields if provided
    if name:
        existing_project.name = name
    if user_id:
        existing_project.user_id = user_id
    if description:
        existing_project.description = description
    if links:
        existing_project.links = links
    
    # Update project in the database
    success = await project_repo.update(existing_project)
    
    if success:
        return {
            "status": "success",
            "message": "Project updated successfully",
            "project_id": project_id
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update project")

