from typing import Dict, Any, List, Optional, Type
from langchain.tools import BaseTool
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

class FormTool(BaseTool):
    name: str = "form_tool"
    description: str = "Tool for managing lease exit workflow forms"
    storage: Storage = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage

    def _run(self, action: str, **kwargs) -> Any:
        """Run the tool with the specified action"""
        actions = {
            "create": self.create_form,
            "validate": self.validate_form,
            "get": self.get_form,
            "process_documents": self.process_documents
        }
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        return actions[action](**kwargs)

    def create_form(self, form_data: Dict[str, Any]) -> str:
        """Create a new form"""
        return self.storage.store_form(form_data)

    def validate_form(self, form_type: str, form_data: Dict[str, Any], 
                     validation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate form data against rules"""
        result = {
            "valid": True,
            "errors": []
        }

        # Check required fields
        required_fields = validation_rules.get("required_fields", [])
        for field in required_fields:
            if field not in form_data:
                result["valid"] = False
                result["errors"].append(f"Missing required field: {field}")

        # Check field types
        field_types = validation_rules.get("field_types", {})
        for field, expected_type in field_types.items():
            if field in form_data:
                value = form_data[field]
                if not isinstance(value, expected_type):
                    result["valid"] = False
                    result["errors"].append(
                        f"Invalid type for field {field}. Expected {expected_type.__name__}"
                    )

        return result

    def get_form(self, form_id: str) -> Dict[str, Any]:
        """Get form details"""
        return self.storage.get_form(form_id)

    def process_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process form documents"""
        # Document processing logic here
        return {
            "processed": True,
            "document_count": len(documents)
        }

    async def _arun(self, *args, **kwargs):
        """Async implementation - not used"""
        raise NotImplementedError("Async not implemented")

class FormTools:
    """Tools for managing forms"""

    def __init__(self):
        self.storage = Storage()
        self.tool = FormTool(self.storage)

    def get_tools(self) -> list:
        """Get all form tools"""
        return [self.tool]