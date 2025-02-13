from crewai import Agent
from typing import Dict, Any, List
from backend.tools.approval_tools import ApprovalTools
from pydantic import Field, ConfigDict

class ApprovalAgent(Agent):
    approval_tool: Any = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        tools = ApprovalTools()
        super().__init__(
            role='Approval Chain Manager',
            goal='Manage approval processes for lease exit workflows',
            backstory="""You are an AI agent responsible for managing the approval 
            chain in lease exit workflows. You track approvals, ensure proper 
            sequencing, and validate completion.""",
            verbose=True,
            allow_delegation=True,
            tools=tools.get_tools()
        )
        self.approval_tool = tools.tool

    def initiate_approval_chain(self, workflow_id: str) -> List[str]:
        """Start the approval chain process"""
        approvers = [
            {"role": "advisory", "order": 1},
            {"role": "ifm", "order": 2},
            {"role": "legal", "order": 3},
            {"role": "mac", "order": 4},
            {"role": "pjm", "order": 5}
        ]

        approval_ids = []
        for approver in approvers:
            approval_id = self.approval_tool._run("create", request_data={
                "workflow_id": workflow_id,
                "approver_role": approver["role"],
                "order": approver["order"],
                "status": "pending"
            })
            if approval_id:
                approval_ids.append(approval_id)

        return approval_ids

    def process_approval(self, workflow_id: str, approver_role: str,
                        decision: str, comments: str = None) -> Dict[str, Any]:
        """Process an approval decision"""
        return self.approval_tool._run("update", approval_data={
            "workflow_id": workflow_id,
            "approver_role": approver_role,
            "decision": decision,
            "comments": comments,
            "timestamp": "now"
        })

    def check_approval_status(self, workflow_id: str) -> Dict[str, Any]:
        """Check the overall status of the approval chain"""
        return self.approval_tool._run("validate", workflow_id=workflow_id)

    def validate_approval_chain(self, workflow_id: str) -> Dict[str, Any]:
        """Validate the approval chain completion and correctness"""
        return self.approval_tool._run("validate", workflow_id=workflow_id)