from crewai import Agent
from backend.tools.workflow_tools import WorkflowTools
from . import create_agent

class WorkflowAgent:
    def __init__(self):
        self.tools = WorkflowTools()
        self.agent = create_agent(
            name="Workflow Orchestrator",
            role="Workflow Management Specialist",
            goal="Manage and orchestrate lease exit workflows efficiently",
            backstory="""I am an expert in managing complex workflows and ensuring 
            smooth process transitions. I understand the lease exit process deeply 
            and can coordinate between different stakeholders.""",
            tools=[
                self.tools.create_workflow(),  # Call methods to get tool instances
                self.tools.update_workflow_state(),
                self.tools.get_workflow_status()
            ]
        )

    def get_agent(self) -> Agent:
        return self.agent