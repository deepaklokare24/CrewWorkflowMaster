from typing import Dict, Any, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from backend.storage import Storage

class ApprovalToolConfig(BaseModel):
    storage: Storage
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ApprovalRequestSchema(BaseModel):
    request_data: Dict[str, Any] = Field(..., description="The approval request data")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ApprovalDecisionSchema(BaseModel):
    approval_id: str = Field(..., description="The ID of the approval to update")
    decision: str = Field(..., description="The decision made on the approval request")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ApprovalIdSchema(BaseModel):
    approval_id: str = Field(..., description="The ID of the approval to check")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class BaseApprovalTool(BaseTool):
    name: str = Field(default="", description="The name of the tool")
    description: str = Field(default="", description="The description of the tool")
    args_schema: Optional[Type[BaseModel]] = Field(default=None, description="The schema for tool arguments")
    config_schema: Type[BaseModel] = Field(default=ApprovalToolConfig, description="The schema for tool configuration")

class CreateApprovalRequestTool(BaseApprovalTool):
    name: str = Field(default="create_approval_request", description="Tool name")
    description: str = Field(default="Creates a new approval request", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=ApprovalRequestSchema, description="Arguments schema")

    def _run(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        approval_id = self.config.storage.create_approval(request_data)
        return {"approval_id": approval_id, "status": "pending"}

    async def _arun(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class ProcessApprovalDecisionTool(BaseApprovalTool):
    name: str = Field(default="process_approval_decision", description="Tool name")
    description: str = Field(default="Processes an approval decision", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=ApprovalDecisionSchema, description="Arguments schema")

    def _run(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        approval_id = kwargs["approval_id"]
        decision = kwargs["decision"]
        success = self.config.storage.update_approval(approval_id, decision)
        return {"success": success, "decision": decision}

    async def _arun(self, **kwargs: Any) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class CheckApprovalStatusTool(BaseApprovalTool):
    name: str = Field(default="check_approval_status", description="Tool name")
    description: str = Field(default="Checks the status of an approval request", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=ApprovalIdSchema, description="Arguments schema")

    def _run(self, approval_id: str) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        return self.config.storage.get_approval(approval_id)

    async def _arun(self, approval_id: str) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class ApprovalTools:
    """Tools for managing approval workflows and decisions"""

    def __init__(self):
        self.storage = Storage()

    def create_approval_request(self) -> BaseTool:
        return CreateApprovalRequestTool(config=ApprovalToolConfig(storage=self.storage))

    def process_approval_decision(self) -> BaseTool:
        return ProcessApprovalDecisionTool(config=ApprovalToolConfig(storage=self.storage))

    def check_approval_status(self) -> BaseTool:
        return CheckApprovalStatusTool(config=ApprovalToolConfig(storage=self.storage))