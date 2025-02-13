from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
from crewai import Crew, Task
import logging
import os
from datetime import datetime

from backend.agents.workflow_agent import WorkflowAgent
from backend.agents.form_agent import FormAgent
from backend.agents.notification_agent import NotificationAgent
from backend.agents.approval_agent import ApprovalAgent
from backend.storage import Storage

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Verify ANTHROPIC_API_KEY
if not os.getenv("ANTHROPIC_API_KEY"):
    logger.error("ANTHROPIC_API_KEY environment variable is not set")
    raise ValueError("ANTHROPIC_API_KEY environment variable must be set")

app = FastAPI()
storage = Storage()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/workflow/lease-exit/create")
async def create_workflow(data: Dict[str, Any]):
    try:
        logger.info(f"Creating workflow with data: {data}")
        workflow_id = storage.create_workflow(data)
        logger.info(f"Workflow created with ID: {workflow_id}")
        return JSONResponse(
            content={"workflow_id": workflow_id, "status": "created"},
            status_code=201
        )
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create workflow: {str(e)}"
        )

@app.get("/api/workflow/lease-exit/{workflow_id}")
async def get_workflow(workflow_id: str):
    try:
        workflow = storage.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow {workflow_id} not found"
            )
        return workflow
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving workflow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve workflow: {str(e)}"
        )

@app.get("/api/workflow/lease-exit/list")
async def list_workflows():
    try:
        logger.info("Fetching all workflows")
        workflows = storage.get_all_workflows()
        logger.info(f"Found {len(workflows) if workflows else 0} workflows")
        return workflows if workflows else []
    except Exception as e:
        logger.error(f"Error fetching workflows: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch workflows: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)