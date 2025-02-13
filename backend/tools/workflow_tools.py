from typing import Dict, Any, Optional, Type
from langchain.tools import BaseTool
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

class WorkflowTool(BaseTool):
    name: str = "workflow_tool"
    description: str = "Tool for managing lease exit workflows"
    storage: Storage = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage

    def _run(self, action: str, **kwargs) -> Any:
        """Run the tool with the specified action"""
        actions = {
            "create": self.create_workflow,
            "update": self.update_workflow,
            "get": self.get_workflow,
            "validate": self.validate_workflow,
            "list": self.list_workflows
        }
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        return actions[action](**kwargs)

    def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create a new workflow instance"""
        return self.storage.create_workflow(workflow_data)

    def update_workflow(self, workflow_id: str, update_data: Dict[str, Any]) -> bool:
        """Update workflow state and data"""
        return self.storage.update_workflow_state(workflow_id, update_data.get("state"))

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow details"""
        return self.storage.get_workflow(workflow_id)

    def validate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Validate workflow state and requirements"""
        workflow = self.storage.get_workflow(workflow_id)
        if not workflow:
            return {"valid": False, "errors": ["Workflow not found"]}

        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Validate required forms
        required_forms = {
            "initial_form": "Initial Lease Exit Form",
            "lease_requirements": "Lease Requirements & Cost Information",
            "exit_requirements_ifm": "IFM Exit Requirements",
            "exit_requirements_mac": "MAC Exit Requirements",
            "exit_requirements_pjm": "PJM Exit Requirements"
        }

        submitted_forms = {form.get("form_type"): True for form in workflow.get("forms", [])}
        
        for form_type, form_name in required_forms.items():
            if form_type not in submitted_forms:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required form: {form_name}")

        # Validate approvals if in approval state
        if workflow.get("current_step") == "approval_chain":
            approvals = workflow.get("approvals", [])
            required_approvers = ["advisory", "ifm", "legal", "mac", "pjm"]
            
            for approver in required_approvers:
                if not any(a.get("approver_role") == approver and a.get("status") == "approved" 
                          for a in approvals):
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Missing approval from {approver.upper()}")

        return validation_result

    def list_workflows(self, filters: Dict[str, Any] = None) -> list:
        """List workflows with optional filtering"""
        workflows = self.storage.get_all_workflows()
        
        if not filters:
            return workflows

        filtered_workflows = []
        for workflow in workflows:
            matches = True
            for key, value in filters.items():
                if workflow.get(key) != value:
                    matches = False
                    break
            if matches:
                filtered_workflows.append(workflow)

        return filtered_workflows

    async def _arun(self, *args, **kwargs):
        """Async implementation - not used"""
        raise NotImplementedError("Async not implemented")

class WorkflowTools:
    """Tools for managing lease exit workflows"""

    def __init__(self):
        self.storage = Storage()
        self.tool = WorkflowTool(self.storage)

    def get_tools(self) -> list:
        """Get all workflow tools"""
        return [self.tool]