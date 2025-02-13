from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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
    allow_origins=["*"],  # In production, this should be more specific
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

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

@app.post("/api/forms/submit")
async def submit_form(form_data: Dict[str, Any]):
    try:
        form_id = storage.store_form(form_data)
        return JSONResponse(
            content={"form_id": form_id, "status": "submitted"},
            status_code=201
        )
    except Exception as e:
        logger.error(f"Error submitting form: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit form: {str(e)}"
        )

@app.post("/api/notifications/send")
async def send_notification(notification_data: Dict[str, Any]):
    try:
        notification_id = storage.store_notification(notification_data)
        return JSONResponse(
            content={"notification_id": notification_id, "status": "sent"},
            status_code=201
        )
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send notification: {str(e)}"
        )

@app.post("/api/approvals/request")
async def create_approval_request(request_data: Dict[str, Any]):
    try:
        approval_id = storage.create_approval(request_data)
        return JSONResponse(
            content={"approval_id": approval_id, "status": "pending"},
            status_code=201
        )
    except Exception as e:
        logger.error(f"Error creating approval request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create approval request: {str(e)}"
        )

@app.get("/api/workflow/lease-exit/list")
async def list_workflows():
    try:
        logger.info("Fetching all workflows")
        workflows = storage.get_all_workflows()
        return JSONResponse(content=workflows)
    except Exception as e:
        logger.error(f"Error fetching workflows: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch workflows: {str(e)}"
        )

try:
    # Initialize agents
    logger.info("Initializing agents...")
    workflow_agent = WorkflowAgent()
    form_agent = FormAgent()
    notification_agent = NotificationAgent()
    approval_agent = ApprovalAgent()

    # Create tasks with expected outputs
    tasks = [
        Task(
            description="Process new lease exit workflow",
            expected_output="""A processed workflow with:
                - Validated input data
                - Generated workflow ID
                - Initial state set
                - Required approvals identified""",
            agent=workflow_agent.get_agent(),
        ),
        Task(
            description="Handle form submissions",
            expected_output="""Processed form submission with:
                - Validated form data
                - Stored form content
                - Generated form ID
                - Extracted key information""",
            agent=form_agent.get_agent(),
        ),
        Task(
            description="Manage notifications",
            expected_output="""Managed notifications with:
                - Generated notification content
                - Sent notifications
                - Tracked delivery status
                - Stored notification records""",
            agent=notification_agent.get_agent(),
        ),
        Task(
            description="Process approvals",
            expected_output="""Processed approval with:
                - Created approval request
                - Tracked approval status
                - Updated workflow state
                - Stored approval decision""",
            agent=approval_agent.get_agent(),
        ),
    ]

    # Create crew
    crew = Crew(
        agents=[
            workflow_agent.get_agent(),
            form_agent.get_agent(),
            notification_agent.get_agent(),
            approval_agent.get_agent()
        ],
        tasks=tasks
    )
    logger.info("Crew initialized successfully")
except Exception as e:
    logger.error(f"Error initializing agents: {str(e)}")
    raise

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)