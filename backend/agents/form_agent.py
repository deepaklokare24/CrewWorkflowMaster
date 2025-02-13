from crewai import Agent
from backend.tools.form_tools import FormTools
from . import create_agent

class FormAgent:
    def __init__(self):
        self.tools = FormTools()
        self.agent = create_agent(
            name="Form Processor",
            role="Form Processing Specialist",
            goal="Process and validate form submissions for lease exit workflows",
            backstory="""I am specialized in handling form data, ensuring accuracy 
            and completeness of submissions. I can extract key information and 
            validate against business rules.""",
            tools=[
                self.tools.validate_form(),  # Call methods to get tool instances
                self.tools.process_form(),
                self.tools.extract_form_data()
            ]
        )

    def get_agent(self) -> Agent:
        return self.agent