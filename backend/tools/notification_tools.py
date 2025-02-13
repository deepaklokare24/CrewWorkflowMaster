from typing import Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from backend.storage import Storage

class NotificationDataSchema(BaseModel):
    notification_data: Dict[str, Any] = Field(..., description="The notification data to process")

class NotificationIdSchema(BaseModel):
    notification_id: str = Field(..., description="The ID of the notification to retrieve")

class NotificationContextSchema(BaseModel):
    context: Dict[str, Any] = Field(..., description="The context for generating notification content")

class NotificationTools:
    def __init__(self):
        self.storage = Storage()

    def send_notification(self) -> BaseTool:
        async def _execute(notification_data: Dict[str, Any]) -> Dict[str, Any]:
            notification_id = self.storage.store_notification(notification_data)
            return {"notification_id": notification_id, "status": "sent"}

        return BaseTool(
            name="send_notification",
            description="Sends notifications to stakeholders",
            args_schema=NotificationDataSchema,
            func=_execute
        )

    def create_notification_content(self) -> BaseTool:
        async def _execute(context: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "subject": f"Update: {context.get('type', 'Lease Exit')} Workflow",
                "content": f"Action required for workflow {context.get('workflow_id')}"
            }

        return BaseTool(
            name="create_notification_content",
            description="Generates notification content based on context",
            args_schema=NotificationContextSchema,
            func=_execute
        )

    def track_notification_status(self) -> BaseTool:
        async def _execute(notification_id: str) -> Dict[str, Any]:
            return self.storage.get_notification(notification_id)

        return BaseTool(
            name="track_notification_status",
            description="Tracks the status of sent notifications",
            args_schema=NotificationIdSchema,
            func=_execute
        )