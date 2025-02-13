from typing import Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from backend.storage import Storage

class CreateWorkflowSchema(BaseModel):
    lease_data: Dict[str, Any] = Field(
        ...,
        description="The lease data required to create a workflow"
    )

class UpdateWorkflowSchema(BaseModel):
    workflow_id: str = Field(..., description="The ID of the workflow to update")
    new_state: str = Field(..., description="The new state to set for the workflow")

class GetWorkflowSchema(BaseModel):
    workflow_id: str = Field(..., description="The ID of the workflow to retrieve")

class WorkflowTools:
    def __init__(self):
        self.storage = Storage()

    def create_workflow(self) -> BaseTool:
        async def _execute(lease_data: Dict[str, Any]) -> Dict[str, Any]:
            workflow_id = self.storage.create_workflow(lease_data)
            return {"workflow_id": workflow_id, "status": "created"}

        return BaseTool(
            name="create_workflow",
            description="Creates a new lease exit workflow",
            args_schema=CreateWorkflowSchema,
            func=_execute
        )

    def update_workflow_state(self) -> BaseTool:
        async def _execute(workflow_id: str, new_state: str) -> Dict[str, Any]:
            success = self.storage.update_workflow_state(workflow_id, new_state)
            return {"success": success, "new_state": new_state}

        return BaseTool(
            name="update_workflow_state",
            description="Updates the state of an existing workflow",
            args_schema=UpdateWorkflowSchema,
            func=_execute
        )

    def get_workflow_status(self) -> BaseTool:
        async def _execute(workflow_id: str) -> Dict[str, Any]:
            return self.storage.get_workflow(workflow_id)

        return BaseTool(
            name="get_workflow_status",
            description="Retrieves the current status of a workflow",
            args_schema=GetWorkflowSchema,
            func=_execute
        )