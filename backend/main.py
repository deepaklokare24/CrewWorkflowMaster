from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Any
from crewai import Crew, Task
import logging
import os

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

# Configure CORS with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

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

@app.post("/api/workflow/lease-exit/create")
async def create_workflow(data: Dict[str, Any]):
    try:
        workflow_id = storage.create_workflow(data)
        return {"workflow_id": workflow_id, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflow/lease-exit/{workflow_id}")
async def get_workflow(workflow_id: str):
    workflow = storage.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.post("/api/forms/submit")
async def submit_form(form_data: Dict[str, Any]):
    try:
        form_id = storage.store_form(form_data)
        return {"form_id": form_id, "status": "submitted"}
    except Exception as e:
        logger.error(f"Error submitting form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notifications/send")
async def send_notification(notification_data: Dict[str, Any]):
    try:
        notification_id = storage.store_notification(notification_data)
        return {"notification_id": notification_id, "status": "sent"}
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/approvals/request")
async def create_approval_request(request_data: Dict[str, Any]):
    try:
        approval_id = storage.create_approval(request_data)
        return {"approval_id": approval_id, "status": "pending"}
    except Exception as e:
        logger.error(f"Error creating approval request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)