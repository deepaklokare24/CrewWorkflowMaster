from typing import Dict, Any, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from backend.storage import Storage

class NotificationToolConfig(BaseModel):
    storage: Storage
    model_config = ConfigDict(arbitrary_types_allowed=True)

class NotificationDataSchema(BaseModel):
    notification_data: Dict[str, Any] = Field(..., description="The notification data to process")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class NotificationIdSchema(BaseModel):
    notification_id: str = Field(..., description="The ID of the notification to retrieve")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class NotificationContextSchema(BaseModel):
    context: Dict[str, Any] = Field(..., description="The context for generating notification content")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class BaseNotificationTool(BaseTool):
    name: str = Field(default="", description="The name of the tool")
    description: str = Field(default="", description="The description of the tool")
    args_schema: Optional[Type[BaseModel]] = Field(default=None, description="The schema for tool arguments")
    config_schema: Type[BaseModel] = Field(default=NotificationToolConfig, description="The schema for tool configuration")

class SendNotificationTool(BaseNotificationTool):
    name: str = Field(default="send_notification", description="Tool name")
    description: str = Field(default="Sends notifications to stakeholders", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=NotificationDataSchema, description="Arguments schema")

    def _run(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        notification_id = self.config.storage.store_notification(notification_data)
        return {"notification_id": notification_id, "status": "sent"}

    async def _arun(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class CreateNotificationContentTool(BaseNotificationTool):
    name: str = Field(default="create_notification_content", description="Tool name")
    description: str = Field(default="Generates notification content based on context", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=NotificationContextSchema, description="Arguments schema")

    def _run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        return {
            "subject": f"Update: {context.get('type', 'Lease Exit')} Workflow",
            "content": f"Action required for workflow {context.get('workflow_id')}"
        }

    async def _arun(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class TrackNotificationStatusTool(BaseNotificationTool):
    name: str = Field(default="track_notification_status", description="Tool name")
    description: str = Field(default="Tracks the status of sent notifications", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=NotificationIdSchema, description="Arguments schema")

    def _run(self, notification_id: str) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        return self.config.storage.get_notification(notification_id)

    async def _arun(self, notification_id: str) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class NotificationTools:
    """Tools for managing notifications and communication"""

    def __init__(self):
        self.storage = Storage()

    def send_notification(self) -> BaseTool:
        return SendNotificationTool(config=NotificationToolConfig(storage=self.storage))

    def create_notification_content(self) -> BaseTool:
        return CreateNotificationContentTool(config=NotificationToolConfig(storage=self.storage))

    def track_notification_status(self) -> BaseTool:
        return TrackNotificationStatusTool(config=NotificationToolConfig(storage=self.storage))