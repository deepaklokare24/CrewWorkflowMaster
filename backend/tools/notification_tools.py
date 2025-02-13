from typing import Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from backend.storage import Storage

class NotificationTool(BaseTool):
    name: str = "notification_tool"
    description: str = "Tool for managing workflow notifications"
    storage: Storage = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage

    def _run(self, action: str, **kwargs) -> Any:
        """Run the tool with the specified action"""
        actions = {
            "send": self.send_notification,
            "get": self.get_notification,
            "update": self.update_notification
        }
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        return actions[action](**kwargs)

    def send_notification(self, notification_data: Dict[str, Any]) -> str:
        """Send a new notification"""
        return self.storage.store_notification(notification_data)

    def get_notification(self, notification_id: str) -> Dict[str, Any]:
        """Get notification details"""
        return self.storage.get_notification(notification_id)

    def update_notification(self, notification_id: str, status: str) -> bool:
        """Update notification status"""
        notification = self.storage.get_notification(notification_id)
        if notification:
            notification["status"] = status
            return True
        return False

    async def _arun(self, *args, **kwargs):
        """Async implementation - not used"""
        raise NotImplementedError("Async not implemented")

class NotificationTools:
    """Tools for managing notifications"""

    def __init__(self):
        self.storage = Storage()
        self.tool = NotificationTool(self.storage)

    def get_tools(self) -> list:
        """Get all notification tools"""
        return [self.tool]