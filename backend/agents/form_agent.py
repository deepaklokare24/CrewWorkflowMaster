from crewai import Agent
from typing import Dict, Any
from backend.tools.form_tools import FormTools
from pydantic import Field, ConfigDict

class FormAgent(Agent):
    form_tool: Any = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        tools = FormTools()
        super().__init__(
            role='Form Processing Specialist',
            goal='Process and validate lease exit related forms and documents',
            backstory="""You are an AI agent specialized in processing and validating 
            various forms related to lease exit workflows. You ensure all required 
            information is provided and properly formatted.""",
            verbose=True,
            allow_delegation=True,
            tools=tools.get_tools()
        )
        self.form_tool = tools.tool

    def process_initial_form(self, workflow_id: str, form_data: Dict[str, Any]) -> str:
        """Process the initial lease exit form"""
        return self.form_tool._run("create", form_data={
            "workflow_id": workflow_id,
            "form_type": "initial_form",
            "data": form_data
        })

    def process_lease_requirements(self, workflow_id: str, form_data: Dict[str, Any], documents: list) -> str:
        """Process lease requirements and cost information form"""
        return self.form_tool._run("create", form_data={
            "workflow_id": workflow_id,
            "form_type": "lease_requirements",
            "data": form_data,
            "documents": documents
        })

    def process_exit_requirements(self, workflow_id: str, form_data: Dict[str, Any], 
                                department: str) -> str:
        """Process exit requirements form for different departments"""
        form_type = f"exit_requirements_{department.lower()}"
        return self.form_tool._run("create", form_data={
            "workflow_id": workflow_id,
            "form_type": form_type,
            "data": form_data
        })

    def validate_form_data(self, form_type: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate form data based on form type"""
        validation_rules = {
            "initial_form": {
                "required_fields": ["lease_id", "exit_date", "reason"],
                "field_types": {
                    "lease_id": str,
                    "exit_date": str,
                    "reason": str
                }
            },
            "lease_requirements": {
                "required_fields": ["cost_estimate", "requirements_list"],
                "field_types": {
                    "cost_estimate": float,
                    "requirements_list": list
                }
            },
            "exit_requirements_ifm": {
                "required_fields": ["scope_details", "timeline"],
                "field_types": {
                    "scope_details": dict,
                    "timeline": str
                }
            },
            "exit_requirements_mac": {
                "required_fields": ["maintenance_details", "equipment_list"],
                "field_types": {
                    "maintenance_details": str,
                    "equipment_list": list
                }
            },
            "exit_requirements_pjm": {
                "required_fields": ["project_plan", "resource_allocation"],
                "field_types": {
                    "project_plan": dict,
                    "resource_allocation": dict
                }
            }
        }

        return self.form_tool._run("validate", 
                                 form_type=form_type,
                                 form_data=form_data,
                                 validation_rules=validation_rules.get(form_type, {}))