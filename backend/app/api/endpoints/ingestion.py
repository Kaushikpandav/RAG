from fastapi import APIRouter, BackgroundTasks
from app.ingestion.pipeline import run_ingestion
import asyncio

router = APIRouter()

@router.post("/trigger")
async def trigger_ingestion(background_tasks: BackgroundTasks):
    """
    Trigger the knowledge base ingestion process in the background.
    """
    # Create a wrapper for the async function to run in background tasks
    # FastAPI BackgroundTasks runs sync functions in a threadpool, 
    # but for async, we should use standard asyncio.create_task or similar if running broadly.
    # However, FastAPI's BackgroundTasks can accept async functions? Yes, starting from newer versions.
    # But to be safe, we'll wrapper it.
    
    # Actually, let's just use asyncio.create_task(run_ingestion()) directly inside the handler 
    # since we want it to run detached from the request.
    
    task = asyncio.create_task(run_ingestion())
    return {"status": "Ingestion started in background"}
