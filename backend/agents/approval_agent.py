from crewai import Agent
from backend.tools.approval_tools import ApprovalTools
from . import create_agent

class ApprovalAgent:
    def __init__(self):
        self.tools = ApprovalTools()
        self.agent = create_agent(
            name="Approval Chain Manager",
            role="Approval Process Specialist",
            goal="Manage approval workflows and track decisions",
            backstory="""I specialize in managing approval chains, ensuring 
            proper authorization flows, and tracking decision states throughout 
            the lease exit process.""",
            tools=[
                self.tools.create_approval_request(),  # Call methods to get tool instances
                self.tools.process_approval_decision(),
                self.tools.check_approval_status()
            ]
        )

    def get_agent(self) -> Agent:
        return self.agent