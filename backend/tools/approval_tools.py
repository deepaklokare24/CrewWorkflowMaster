from typing import Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from backend.storage import Storage

class ApprovalRequestSchema(BaseModel):
    request_data: Dict[str, Any] = Field(..., description="The approval request data")

class ApprovalDecisionSchema(BaseModel):
    approval_id: str = Field(..., description="The ID of the approval to update")
    decision: str = Field(..., description="The decision made on the approval request")

class ApprovalIdSchema(BaseModel):
    approval_id: str = Field(..., description="The ID of the approval to check")

class ApprovalTools:
    def __init__(self):
        self.storage = Storage()

    def create_approval_request(self) -> BaseTool:
        async def _execute(request_data: Dict[str, Any]) -> Dict[str, Any]:
            approval_id = self.storage.create_approval(request_data)
            return {"approval_id": approval_id, "status": "pending"}

        return BaseTool(
            name="create_approval_request",
            description="Creates a new approval request",
            args_schema=ApprovalRequestSchema,
            func=_execute
        )

    def process_approval_decision(self) -> BaseTool:
        async def _execute(approval_id: str, decision: str) -> Dict[str, Any]:
            success = self.storage.update_approval(approval_id, decision)
            return {"success": success, "decision": decision}

        return BaseTool(
            name="process_approval_decision",
            description="Processes an approval decision",
            args_schema=ApprovalDecisionSchema,
            func=_execute
        )

    def check_approval_status(self) -> BaseTool:
        async def _execute(approval_id: str) -> Dict[str, Any]:
            return self.storage.get_approval(approval_id)

        return BaseTool(
            name="check_approval_status",
            description="Checks the status of an approval request",
            args_schema=ApprovalIdSchema,
            func=_execute
        )