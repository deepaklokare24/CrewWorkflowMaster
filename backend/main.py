from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from typing import Dict, Any, List
import logging
import os
from datetime import datetime
import asyncio
from collections import defaultdict
import json

from agents import LeaseExitCrew
from storage import Storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable verbose logging for CrewAI
os.environ["CREWAI_LOGGING"] = "1"
os.environ["LANGCHAIN_VERBOSE"] = "true"

# Verify ANTHROPIC_API_KEY
if not os.getenv("ANTHROPIC_API_KEY"):
    logger.error("ANTHROPIC_API_KEY environment variable is not set")
    raise ValueError("ANTHROPIC_API_KEY environment variable must be set")

app = FastAPI(title="Flow.AI - Lease Exit Workflow Management")
storage = Storage()

# Store connected clients
workflow_clients = defaultdict(set)

# Configure CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize CrewAI
lease_exit_crew = LeaseExitCrew()

async def send_workflow_update(workflow_id: str, data: Dict[str, Any]):
    """Send update to all clients subscribed to a workflow"""
    if workflow_id in workflow_clients:
        message = {
            "workflow_id": workflow_id,
            "type": "workflow_update",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        for queue in workflow_clients[workflow_id]:
            await queue.put(message)

async def event_generator(workflow_id: str, queue: asyncio.Queue):
    """Generate SSE events for a workflow"""
    try:
        # Send initial state
        progress = storage.get_workflow_progress(workflow_id)
        if progress:
            yield {
                "event": "message",
                "data": json.dumps({
                    "workflow_id": workflow_id,
                    "type": "initial_state",
                    "data": progress,
                    "timestamp": datetime.now().isoformat()
                })
            }
        
        # Wait for updates
        while True:
            data = await queue.get()
            if isinstance(data, dict):
                yield {
                    "event": "message",
                    "data": json.dumps(data)
                }
            else:
                yield {
                    "event": "message",
                    "data": data
                }
    except asyncio.CancelledError:
        logger.info(f"Client disconnected from workflow {workflow_id}")
        raise
    finally:
        workflow_clients[workflow_id].remove(queue)
        if not workflow_clients[workflow_id]:
            del workflow_clients[workflow_id]

@app.get("/api/workflow/lease-exit/{workflow_id}/events")
async def workflow_events(workflow_id: str):
    """SSE endpoint for workflow progress updates"""
    try:
        logger.info(f"Client connected to workflow events for {workflow_id}")
        queue = asyncio.Queue()
        workflow_clients[workflow_id].add(queue)
        
        return EventSourceResponse(
            event_generator(workflow_id, queue),
            ping=20,  # Send ping every 20 seconds to keep connection alive
        )
    except Exception as e:
        logger.error(f"Error in workflow events: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to establish event stream: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/workflow/lease-exit/create")
async def create_workflow(data: Dict[str, Any]):
    try:
        logger.info(f"Creating new workflow with data: {data}")
        
        # Create initial workflow record
        workflow_data = {
            "property_name": data.get("propertyName"),
            "property_type": data.get("propertyType", "Commercial"),
            "lease_end_date": data.get("leaseEndDate"),
            "exit_reason": data.get("exitReason"),
            "submitted_by": data.get("submittedBy", "user"),
            "state": "draft",
            "current_step": "initial",
            "created_at": datetime.now().isoformat()
        }
        
        # Store initial workflow
        workflow_id = storage.create_workflow(workflow_data)
        
        # Send initial update to subscribers
        await send_workflow_update(workflow_id, {
            "state": "draft",
            "current_step": "initial",
            "message": "Workflow created"
        })
        
        # Prepare inputs for CrewAI
        crew_inputs = {
            **workflow_data,
            "workflow_id": workflow_id
        }
        
        # Validate inputs
        crew_inputs = lease_exit_crew.validate_inputs(crew_inputs)
        
        # Create workflow task
        workflow_task = lease_exit_crew.create_workflow_task(crew_inputs)
        
        # Execute CrewAI workflow
        logger.info("Executing CrewAI workflow")
        crew = lease_exit_crew.crew()
        crew.tasks = [workflow_task]  # Set the task for this workflow
        result = crew.kickoff()
        logger.info(f"CrewAI workflow completed: {result}")
        
        # Process results
        processed_result = lease_exit_crew.process_results(result)
        
        # Update workflow state
        update_data = {
            "state": "in_progress",
            "current_step": "advisory_review",
            "crew_result": processed_result
        }
        storage.update_workflow_state(workflow_id, update_data)
        
        # Send update to subscribers
        await send_workflow_update(workflow_id, {
            **update_data,
            "message": "Workflow initialized and in progress"
        })
        
        return JSONResponse(
            content={
                "workflow_id": workflow_id,
                "status": "created",
                "state": "in_progress",
                "current_step": "advisory_review",
                "crew_result": processed_result
            },
            status_code=201
        )
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create workflow: {str(e)}"
        )

@app.post("/api/workflow/lease-exit/{workflow_id}/form")
async def submit_form(workflow_id: str, form_data: Dict[str, Any]):
    try:
        logger.info(f"Processing form submission for workflow {workflow_id}")
        
        # Prepare inputs for CrewAI
        crew_inputs = {
            "workflow_id": workflow_id,
            "form_type": form_data.get("formType"),
            "submitted_by": form_data.get("submittedBy"),
            "form_data": form_data
        }
        
        # Create form processing task
        form_task = lease_exit_crew.process_form_task(crew_inputs)
        
        # Execute CrewAI form processing
        logger.info("Executing CrewAI form processing")
        crew = lease_exit_crew.crew()
        crew.tasks = [form_task]  # Set the task for form processing
        result = crew.kickoff()
        logger.info(f"CrewAI form processing completed: {result}")
        
        # Process results
        processed_result = lease_exit_crew.process_results(result)
        
        return JSONResponse(
            content={"status": "submitted", "result": processed_result},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error submitting form: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit form: {str(e)}"
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

@app.get("/api/workflow/lease-exit/{workflow_id}")
async def get_workflow(workflow_id: str):
    try:
        logger.info(f"Fetching workflow {workflow_id}")
        workflow = storage.get_workflow(workflow_id)
        if not workflow:
            logger.warning(f"Workflow {workflow_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Workflow {workflow_id} not found"
            )
        logger.info(f"Successfully retrieved workflow {workflow_id}")
        return workflow
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving workflow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve workflow: {str(e)}"
        )

@app.get("/api/workflow/lease-exit/{workflow_id}/progress")
async def get_workflow_progress(workflow_id: str):
    """Get detailed progress information for a workflow"""
    try:
        logger.info(f"Fetching progress for workflow {workflow_id}")
        progress = storage.get_workflow_progress(workflow_id)
        if not progress:
            logger.warning(f"Workflow {workflow_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Workflow {workflow_id} not found"
            )
        logger.info(f"Successfully retrieved progress for workflow {workflow_id}")
        return progress
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving workflow progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve workflow progress: {str(e)}"
        )

def _get_form_type(step: str) -> str:
    """Map workflow step to form type"""
    form_type_map = {
        "advisory_review": "lease_requirements",
        "ifm_review": "exit_requirements_ifm",
        "mac_review": "exit_requirements_mac",
        "pjm_review": "exit_requirements_pjm"
    }
    return form_type_map.get(step)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Flow.AI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)