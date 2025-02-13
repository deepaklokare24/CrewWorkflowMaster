from crewai import Agent
from backend.tools.notification_tools import NotificationTools
from . import create_agent

class NotificationAgent:
    def __init__(self):
        self.tools = NotificationTools()
        self.agent = create_agent(
            name="Notification Manager",
            role="Communication Specialist",
            goal="Manage and send notifications to relevant stakeholders",
            backstory="""I handle all communication aspects of the workflow, 
            ensuring the right people are notified at the right time with 
            the right information.""",
            tools=[
                self.tools.send_notification(),  # Call methods to get tool instances
                self.tools.create_notification_content(),
                self.tools.track_notification_status()
            ]
        )

    def get_agent(self) -> Agent:
        return self.agent