"""
Agents package initialization for the Lease Exit Workflow Management System.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, List
from crewai import Agent, Crew, Task
from anthropic import Anthropic
from datetime import datetime
import json
import logging

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

logger = logging.getLogger(__name__)

class LeaseExitCrew:
    """Lease Exit Workflow Management Crew"""

    def __init__(self):
        """Initialize the crew with all necessary agents"""
        self.workflow_agent = self._create_workflow_agent()
        self.form_agent = self._create_form_agent()
        self.notification_agent = self._create_notification_agent()
        self.approval_agent = self._create_approval_agent()

    def _create_workflow_agent(self) -> Agent:
        """Creates the workflow management agent"""
        return Agent(
            role="Lease Exit Workflow Manager",
            goal="Manage and orchestrate lease exit workflows efficiently",
            backstory="""You are an AI agent responsible for managing lease exit workflows. 
            You ensure all steps are followed correctly and stakeholders are properly involved.""",
            verbose=True,
            allow_delegation=True,
            llm_config={
                "client": client,
                "model": "claude-3-sonnet-20240229",
                "temperature": 0.7
            }
        )

    def _create_form_agent(self) -> Agent:
        """Creates the form processing agent"""
        return Agent(
            role="Form Processing Specialist",
            goal="Process and validate lease exit related forms and documents",
            backstory="""You are an AI agent specialized in processing and validating 
            various forms related to lease exit workflows. You ensure all required 
            information is provided and properly formatted.""",
            verbose=True,
            allow_delegation=True,
            llm_config={
                "client": client,
                "model": "claude-3-sonnet-20240229",
                "temperature": 0.7
            }
        )

    def _create_notification_agent(self) -> Agent:
        """Creates the notification management agent"""
        return Agent(
            role="Notification Manager",
            goal="Manage and send notifications for lease exit workflow events",
            backstory="""You are an AI agent responsible for managing communications 
            in the lease exit workflow. You ensure all stakeholders are properly 
            notified of relevant events and actions required.""",
            verbose=True,
            allow_delegation=True,
            llm_config={
                "client": client,
                "model": "claude-3-sonnet-20240229",
                "temperature": 0.7
            }
        )

    def _create_approval_agent(self) -> Agent:
        """Creates the approval chain management agent"""
        return Agent(
            role="Approval Chain Manager",
            goal="Manage approval processes for lease exit workflows",
            backstory="""You are an AI agent responsible for managing the approval 
            chain in lease exit workflows. You track approvals, ensure proper 
            sequencing, and validate completion.""",
            verbose=True,
            allow_delegation=True,
            llm_config={
                "client": client,
                "model": "claude-3-sonnet-20240229",
                "temperature": 0.7
            }
        )

    def create_workflow_task(self, inputs: Dict[str, Any]) -> Task:
        """Creates a task for creating a new workflow"""
        description = f"""Create a new lease exit workflow for {inputs['property_name']}.
        Property Type: {inputs['property_type']}
        Lease End Date: {inputs['lease_end_date']}
        Exit Reason: {inputs['exit_reason']}
        
        Ensure all initial requirements are set up and proper notifications are sent."""
        
        return Task(
            description=description,
            agent=self.workflow_agent,
            expected_output="A dictionary containing the workflow creation status and next steps"
        )

    def process_form_task(self, inputs: Dict[str, Any]) -> Task:
        """Creates a task for processing forms"""
        description = f"""Process and validate the form submission for workflow {inputs['workflow_id']}.
        Form Type: {inputs['form_type']}
        Submitted By: {inputs['submitted_by']}
        
        Ensure all required fields are present and properly formatted."""
        
        return Task(
            description=description,
            agent=self.form_agent,
            expected_output="A dictionary containing the form processing results and validation status"
        )

    def send_notifications_task(self, inputs: Dict[str, Any]) -> Task:
        """Creates a task for sending notifications"""
        description = f"""Send notifications for workflow {inputs['workflow_id']}.
        Event Type: {inputs['event_type']}
        Recipients: {inputs['recipients']}
        
        Ensure proper formatting and delivery of notifications."""
        
        return Task(
            description=description,
            agent=self.notification_agent,
            expected_output="A dictionary containing notification delivery status and recipient information"
        )

    def manage_approvals_task(self, inputs: Dict[str, Any]) -> Task:
        """Creates a task for managing approvals"""
        description = f"""Manage approval process for workflow {inputs['workflow_id']}.
        Current Step: {inputs['current_step']}
        Required Approvers: {inputs['required_approvers']}
        
        Track and validate approval chain completion."""
        
        return Task(
            description=description,
            agent=self.approval_agent,
            expected_output="A dictionary containing approval chain status and decisions"
        )

    def crew(self) -> Crew:
        """Creates and returns a crew for executing tasks"""
        return Crew(
            agents=[
                self.workflow_agent,
                self.form_agent,
                self.notification_agent,
                self.approval_agent
            ],
            tasks=[],  # Tasks will be added based on the specific workflow needs
            verbose=True
        )

    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inputs before crew execution"""
        required_fields = ["property_name", "property_type", "lease_end_date", "exit_reason"]
        for field in required_fields:
            if field not in inputs:
                raise ValueError(f"Missing required field: {field}")
        return inputs

    def process_results(self, result: Any) -> Dict[str, Any]:
        """Process results after crew execution"""
        try:
            # Extract the raw output if it's a CrewOutput object
            if hasattr(result, 'raw'):
                raw_text = result.raw
            elif isinstance(result, str):
                raw_text = result
            else:
                raw_text = str(result)

            # Clean up the output by removing markdown code blocks and extra whitespace
            cleaned_text = raw_text.strip()
            if cleaned_text.startswith('```'):
                # Remove opening code block
                cleaned_text = cleaned_text[cleaned_text.find('\n')+1:]
            if cleaned_text.endswith('```'):
                # Remove closing code block
                cleaned_text = cleaned_text[:cleaned_text.rfind('```')]
            
            # Remove any language identifier (like ```json)
            if cleaned_text.startswith('json\n'):
                cleaned_text = cleaned_text[5:]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse the cleaned JSON
            result_data = json.loads(cleaned_text)

            return {
                "success": True,
                "result": result_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing crew results: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "result": raw_text,
                "timestamp": datetime.now().isoformat()
            }

__all__ = [
    'LeaseExitCrew'
]