from typing import Dict, Any, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from backend.storage import Storage

class WorkflowToolConfig(BaseModel):
    storage: Storage
    model_config = ConfigDict(arbitrary_types_allowed=True)

class CreateWorkflowSchema(BaseModel):
    lease_data: Dict[str, Any] = Field(
        ...,
        description="The lease data required to create a workflow"
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

class UpdateWorkflowSchema(BaseModel):
    workflow_id: str = Field(..., description="The ID of the workflow to update")
    new_state: str = Field(..., description="The new state to set for the workflow")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class GetWorkflowSchema(BaseModel):
    workflow_id: str = Field(..., description="The ID of the workflow to retrieve")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class BaseCRUDTool(BaseTool):
    name: str = Field(default="", description="The name of the tool")
    description: str = Field(default="", description="The description of the tool")
    args_schema: Optional[Type[BaseModel]] = Field(default=None, description="The schema for tool arguments")
    config_schema: Type[BaseModel] = Field(default=WorkflowToolConfig, description="The schema for tool configuration")

class CreateWorkflowTool(BaseCRUDTool):
    name: str = Field(default="create_workflow", description="Tool name")
    description: str = Field(default="Creates a new lease exit workflow", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=CreateWorkflowSchema, description="Arguments schema")

    def _run(self, lease_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        workflow_id = self.config.storage.create_workflow(lease_data)
        return {"workflow_id": workflow_id, "status": "created"}

    async def _arun(self, lease_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class UpdateWorkflowStateTool(BaseCRUDTool):
    name: str = Field(default="update_workflow_state", description="Tool name")
    description: str = Field(default="Updates the state of an existing workflow", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=UpdateWorkflowSchema, description="Arguments schema")

    def _run(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        workflow_id = kwargs["workflow_id"]
        new_state = kwargs["new_state"]
        success = self.config.storage.update_workflow_state(workflow_id, new_state)
        return {"success": success, "new_state": new_state}

    async def _arun(self, **kwargs: Any) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class GetWorkflowStatusTool(BaseCRUDTool):
    name: str = Field(default="get_workflow_status", description="Tool name")
    description: str = Field(default="Retrieves the current status of a workflow", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=GetWorkflowSchema, description="Arguments schema")

    def _run(self, workflow_id: str) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        return self.config.storage.get_workflow(workflow_id)

    async def _arun(self, workflow_id: str) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class WorkflowTools:
    """Tools for managing lease exit workflows"""

    def __init__(self):
        self.storage = Storage()

    def create_workflow(self) -> BaseTool:
        return CreateWorkflowTool(config=WorkflowToolConfig(storage=self.storage))

    def update_workflow_state(self) -> BaseTool:
        return UpdateWorkflowStateTool(config=WorkflowToolConfig(storage=self.storage))

    def get_workflow_status(self) -> BaseTool:
        return GetWorkflowStatusTool(config=WorkflowToolConfig(storage=self.storage))