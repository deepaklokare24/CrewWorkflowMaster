from crewai import Agent
from typing import Dict, Any
from backend.tools.workflow_tools import WorkflowTools
from pydantic import Field, ConfigDict

class WorkflowAgent(Agent):
    workflow_tool: Any = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        tools = WorkflowTools()
        super().__init__(
            role='Workflow Orchestrator',
            goal='Manage and orchestrate lease exit workflows efficiently',
            backstory="""You are an AI agent responsible for managing lease exit workflows. 
            You ensure all steps are followed correctly and stakeholders are properly involved.""",
            verbose=True,
            allow_delegation=True,
            tools=tools.get_tools()
        )
        self.workflow_tool = tools.tool

    def create_lease_exit_workflow(self, lease_data: Dict[str, Any]) -> str:
        """Create a new lease exit workflow instance"""
        return self.workflow_tool._run("create", workflow_data={
            "type": "lease_exit",
            "lease_data": lease_data,
            "state": "draft",
            "current_step": "initial_form"
        })

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow details"""
        return self.workflow_tool._run("get", workflow_id=workflow_id)

    def list_workflows(self, filters: Dict[str, Any] = None) -> list:
        """List all workflows with optional filtering"""
        return self.workflow_tool._run("list", filters=filters)

    def advance_workflow(self, workflow_id: str, form_data: Dict[str, Any]) -> bool:
        """Advance the workflow based on current state and form submission"""
        workflow = self.workflow_tool._run("get", workflow_id=workflow_id)
        if not workflow:
            return False

        current_step = workflow["current_step"]
        next_step = self._determine_next_step(current_step, form_data)
        
        return self.workflow_tool._run("update", workflow_id=workflow_id, update_data={
            "state": "in_progress",
            "current_step": next_step
        })

    def _determine_next_step(self, current_step: str, form_data: Dict[str, Any]) -> str:
        """Determine the next step in the workflow based on current state"""
        step_sequence = {
            "initial_form": "advisory_review",
            "advisory_review": "ifm_review",
            "ifm_review": "mac_review",
            "mac_review": "pjm_review",
            "pjm_review": "management_review",
            "management_review": "approval_chain",
            "approval_chain": "ready_for_exit"
        }
        return step_sequence.get(current_step, current_step)

    def validate_workflow_completion(self, workflow_id: str) -> bool:
        """Validate if all required steps are completed for the workflow"""
        result = self.workflow_tool._run("validate", workflow_id=workflow_id)
        return result.get("valid", False)