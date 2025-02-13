from typing import Dict, Any, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from backend.storage import Storage

class ApprovalTool(BaseTool):
    name: str = "approval_tool"
    description: str = "Tool for managing approval workflows and decisions"
    storage: Storage = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage

    def _run(self, action: str, **kwargs) -> Any:
        """Run the tool with the specified action"""
        actions = {
            "create": self.create_approval,
            "update": self.update_approval,
            "get": self.get_approval,
            "validate": self.validate_approval_chain
        }
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        return actions[action](**kwargs)

    def create_approval(self, request_data: Dict[str, Any]) -> str:
        """Create a new approval request"""
        return self.storage.create_approval(request_data)

    def update_approval(self, approval_id: str, decision: str) -> bool:
        """Update approval decision"""
        return self.storage.update_approval(approval_id, decision)

    def get_approval(self, approval_id: str) -> Dict[str, Any]:
        """Get approval details"""
        return self.storage.get_approval(approval_id)

    def validate_approval_chain(self, workflow_id: str) -> Dict[str, Any]:
        """Validate the approval chain for a workflow"""
        approvals = self.storage.get_workflow(workflow_id).get("approvals", [])
        required_approvers = ["advisory", "ifm", "legal", "mac", "pjm"]
        
        result = {
            "valid": True,
            "errors": [],
            "pending": [],
            "approved": [],
            "rejected": []
        }

        for approver in required_approvers:
            found = False
            for approval in approvals:
                if approval.get("approver_role") == approver:
                    found = True
                    status = approval.get("status")
                    if status == "pending":
                        result["pending"].append(approver)
                    elif status == "approved":
                        result["approved"].append(approver)
                    elif status == "rejected":
                        result["rejected"].append(approver)
                        result["valid"] = False
                    break
            if not found:
                result["errors"].append(f"Missing approval from {approver}")
                result["valid"] = False

        return result

    async def _arun(self, *args, **kwargs):
        """Async implementation - not used"""
        raise NotImplementedError("Async not implemented")

class ApprovalTools:
    """Tools for managing approval workflows and decisions"""

    def __init__(self):
        self.storage = Storage()
        self.tool = ApprovalTool(self.storage)

    def get_tools(self) -> list:
        """Get all approval tools"""
        return [self.tool]