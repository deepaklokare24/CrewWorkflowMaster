from typing import Dict, Any
from crewai import Agent
from anthropic import Anthropic
import os

# Initialize Anthropic client
# Note: the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def create_agent(name: str, role: str, goal: str, backstory: str, tools: list) -> Agent:
    """Helper function to create CrewAI agents with consistent configuration"""
    return Agent(
        name=name,
        role=role,
        goal=goal,
        backstory=backstory,
        tools=tools,
        llm_config={
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.7,
            "client": client
        }
    )

# Import agent classes
from .workflow_agent import WorkflowAgent
from .form_agent import FormAgent
from .notification_agent import NotificationAgent
from .approval_agent import ApprovalAgent

__all__ = [
    'create_agent',
    'WorkflowAgent',
    'FormAgent',
    'NotificationAgent',
    'ApprovalAgent'
]