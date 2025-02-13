from typing import Dict, Any, List, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from backend.storage import Storage

class FormToolConfig(BaseModel):
    storage: Storage
    model_config = ConfigDict(arbitrary_types_allowed=True)

class FormDataSchema(BaseModel):
    form_data: Dict[str, Any] = Field(..., description="The form data to process")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class FormIdSchema(BaseModel):
    form_id: str = Field(..., description="The ID of the form to retrieve")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class BaseFormTool(BaseTool):
    name: str = Field(default="", description="The name of the tool")
    description: str = Field(default="", description="The description of the tool")
    args_schema: Optional[Type[BaseModel]] = Field(default=None, description="The schema for tool arguments")
    config_schema: Type[BaseModel] = Field(default=FormToolConfig, description="The schema for tool configuration")

class ValidateFormTool(BaseFormTool):
    name: str = Field(default="validate_form", description="Tool name")
    description: str = Field(default="Validates form data against business rules", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=FormDataSchema, description="Arguments schema")

    def _run(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        # Implement form validation logic
        is_valid = True  # Add actual validation
        return {"is_valid": is_valid, "errors": []}

    async def _arun(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class ProcessFormTool(BaseFormTool):
    name: str = Field(default="process_form", description="Tool name")
    description: str = Field(default="Processes and stores form submissions", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=FormDataSchema, description="Arguments schema")

    def _run(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        form_id = self.config.storage.store_form(form_data)
        return {"form_id": form_id, "status": "processed"}

    async def _arun(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class ExtractFormDataTool(BaseFormTool):
    name: str = Field(default="extract_form_data", description="Tool description")
    description: str = Field(default="Extracts key information from form submissions", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=FormIdSchema, description="Arguments schema")

    def _run(self, form_id: str) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        return self.config.storage.get_form(form_id)

    async def _arun(self, form_id: str) -> Dict[str, Any]:
        """Async implementation"""
        raise NotImplementedError("Async run not implemented")

class FormTools:
    """Tools for handling form submissions and validation"""

    def __init__(self):
        self.storage = Storage()

    def validate_form(self) -> BaseTool:
        return ValidateFormTool(config=FormToolConfig(storage=self.storage))

    def process_form(self) -> BaseTool:
        return ProcessFormTool(config=FormToolConfig(storage=self.storage))

    def extract_form_data(self) -> BaseTool:
        return ExtractFormDataTool(config=FormToolConfig(storage=self.storage))