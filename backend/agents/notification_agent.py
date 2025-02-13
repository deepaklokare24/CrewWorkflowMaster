from crewai import Agent
from typing import Dict, Any, List
from backend.tools.notification_tools import NotificationTools
from pydantic import Field, ConfigDict

class NotificationAgent(Agent):
    notification_tool: Any = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        tools = NotificationTools()
        super().__init__(
            role='Notification Manager',
            goal='Manage and send notifications for lease exit workflow events',
            backstory="""You are an AI agent responsible for managing communications 
            in the lease exit workflow. You ensure all stakeholders are properly 
            notified of relevant events and actions required.""",
            verbose=True,
            allow_delegation=True,
            tools=tools.get_tools()
        )
        self.notification_tool = tools.tool

    def notify_form_submission(self, workflow_id: str, form_type: str, 
                             submitted_by: str) -> str:
        """Notify relevant stakeholders about form submission"""
        notification_map = {
            "initial_form": ["advisory", "ifm", "legal"],
            "lease_requirements": ["legal", "ifm", "accounting"],
            "exit_requirements_ifm": ["mac"],
            "exit_requirements_mac": ["pjm"],
            "exit_requirements_pjm": ["lease_exit_team"]
        }

        recipients = notification_map.get(form_type, [])
        if not recipients:
            return None

        return self.notification_tool._run("send", notification_data={
            "workflow_id": workflow_id,
            "type": "form_submission",
            "recipients": recipients,
            "data": {
                "form_type": form_type,
                "submitted_by": submitted_by,
                "timestamp": "now"
            }
        })

    def notify_approval_required(self, workflow_id: str, approvers: List[str]) -> List[str]:
        """Send approval request notifications"""
        notification_ids = []
        for approver in approvers:
            notification_id = self.notification_tool._run("send", notification_data={
                "workflow_id": workflow_id,
                "type": "approval_required",
                "recipients": [approver],
                "data": {
                    "action_required": "approve_or_reject",
                    "timestamp": "now"
                }
            })
            if notification_id:
                notification_ids.append(notification_id)
        return notification_ids

    def notify_workflow_status(self, workflow_id: str, status: str, 
                             recipients: List[str]) -> str:
        """Notify about workflow status changes"""
        status_messages = {
            "ready_for_approval": "Workflow is ready for final approval",
            "approved": "Workflow has been approved by all stakeholders",
            "rejected": "Workflow requires revision - some approvals were rejected",
            "ready_for_exit": "Workflow is complete and ready for lease exit",
            "completed": "Lease exit process has been completed"
        }

        return self.notification_tool._run("send", notification_data={
            "workflow_id": workflow_id,
            "type": "status_update",
            "recipients": recipients,
            "data": {
                "status": status,
                "message": status_messages.get(status, "Status updated"),
                "timestamp": "now"
            }
        })

    def notify_revision_needed(self, workflow_id: str, rejected_by: str, 
                             comments: str) -> str:
        """Notify about required workflow revision"""
        return self.notification_tool._run("send", notification_data={
            "workflow_id": workflow_id,
            "type": "revision_required",
            "recipients": ["lease_exit_team"],
            "data": {
                "rejected_by": rejected_by,
                "comments": comments,
                "timestamp": "now"
            }
        })