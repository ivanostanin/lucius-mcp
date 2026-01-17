import typing

from pydantic import BaseModel


def generate_schema_hint(model: type[BaseModel]) -> str:
    """
    Generates a simplified schema usage hint for a Pydantic model.
    Used to guide Agents when they provide invalid input.
    """
    if not model or not issubclass(model, BaseModel):
        return ""

    lines = ["Schema Hint (Expected Format):"]

    for name, field in model.model_fields.items():
        type_name = _get_type_name(field.annotation)
        req_marker = "required" if field.is_required() else "optional"

        # Handle enums in description if possible
        # Pydantic v2 stores simplified repr, we might want to be explicit

        # Use alias if available for better JSON matching
        display_name = field.alias or name

        lines.append(f"- {display_name}: {type_name} ({req_marker})")

    return "\n".join(lines)


def _get_type_name(annotation: typing.Any) -> str:
    """Helper to maintain readable type names."""
    if annotation is None:
        return "Any"

    # Handle Optional[X] -> X | None
    # Handle List[X] -> list[X]
    # Simple stringification usually works well enough for hints
    s = str(annotation)
    s = s.replace("typing.", "")
    s = s.replace("<class '", "").replace("'>", "")

    # Simplify Pydantic Strict types / Annotated
    if "Annotated[" in s:
        # Extract the inner type: Annotated[int, ...] -> int
        # Regex or simple string manipulation
        # Basic heuristic: take text between [ and ,
        start = s.find("[")
        end = s.find(",")
        if start != -1 and end != -1:
            s = s[start + 1 : end].strip()

    # Clean up common Pydantic/Python types
    s = s.replace("StrictInt", "int")
    s = s.replace("StrictStr", "str")
    s = s.replace("StrictBool", "bool")

    return s
