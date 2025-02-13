from typing import Dict, Any
import json
from datetime import datetime

class Storage:
    """Simple in-memory storage for MVP"""
    
    def __init__(self):
        self.workflows = {}
        self.forms = {}
        self.notifications = {}
        self.approvals = {}

    def create_workflow(self, data: Dict[str, Any]) -> str:
        workflow_id = f"wf_{datetime.now().timestamp()}"
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "data": data,
            "state": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return workflow_id

    def update_workflow_state(self, workflow_id: str, new_state: str) -> bool:
        if workflow_id in self.workflows:
            self.workflows[workflow_id]["state"] = new_state
            self.workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
            return True
        return False

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        return self.workflows.get(workflow_id, {})

    def store_form(self, form_data: Dict[str, Any]) -> str:
        form_id = f"form_{datetime.now().timestamp()}"
        self.forms[form_id] = {
            "id": form_id,
            "data": form_data,
            "created_at": datetime.now().isoformat()
        }
        return form_id

    def get_form(self, form_id: str) -> Dict[str, Any]:
        return self.forms.get(form_id, {})

    def store_notification(self, notification_data: Dict[str, Any]) -> str:
        notification_id = f"notif_{datetime.now().timestamp()}"
        self.notifications[notification_id] = {
            "id": notification_id,
            "data": notification_data,
            "status": "sent",
            "created_at": datetime.now().isoformat()
        }
        return notification_id

    def get_notification(self, notification_id: str) -> Dict[str, Any]:
        return self.notifications.get(notification_id, {})

    def create_approval(self, request_data: Dict[str, Any]) -> str:
        approval_id = f"appr_{datetime.now().timestamp()}"
        self.approvals[approval_id] = {
            "id": approval_id,
            "data": request_data,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return approval_id

    def update_approval(self, approval_id: str, decision: str) -> bool:
        if approval_id in self.approvals:
            self.approvals[approval_id]["status"] = decision
            self.approvals[approval_id]["updated_at"] = datetime.now().isoformat()
            return True
        return False

    def get_approval(self, approval_id: str) -> Dict[str, Any]:
        return self.approvals.get(approval_id, {})
