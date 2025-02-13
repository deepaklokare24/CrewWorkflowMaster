from typing import Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from backend.storage import Storage

class FormDataSchema(BaseModel):
    form_data: Dict[str, Any] = Field(..., description="The form data to process")

class FormIdSchema(BaseModel):
    form_id: str = Field(..., description="The ID of the form to retrieve")

class FormTools:
    def __init__(self):
        self.storage = Storage()

    def validate_form(self) -> BaseTool:
        async def _execute(form_data: Dict[str, Any]) -> Dict[str, Any]:
            # Implement form validation logic
            is_valid = True  # Add actual validation
            return {"is_valid": is_valid, "errors": []}

        return BaseTool(
            name="validate_form",
            description="Validates form data against business rules",
            args_schema=FormDataSchema,
            func=_execute
        )

    def process_form(self) -> BaseTool:
        async def _execute(form_data: Dict[str, Any]) -> Dict[str, Any]:
            form_id = self.storage.store_form(form_data)
            return {"form_id": form_id, "status": "processed"}

        return BaseTool(
            name="process_form",
            description="Processes and stores form submissions",
            args_schema=FormDataSchema,
            func=_execute
        )

    def extract_form_data(self) -> BaseTool:
        async def _execute(form_id: str) -> Dict[str, Any]:
            return self.storage.get_form(form_id)

        return BaseTool(
            name="extract_form_data",
            description="Extracts key information from form submissions",
            args_schema=FormIdSchema,
            func=_execute
        )