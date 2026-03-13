import types
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

    normalized = _normalize_type_name(annotation)
    if normalized is not None:
        return normalized

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
        if start != -1:
            if end == -1:
                end = s.rfind("]")
            if end != -1 and end > start:
                s = s[start + 1 : end].strip()

    # Clean up common Pydantic/Python types
    s = s.replace("StrictInt", "int")
    s = s.replace("StrictStr", "str")
    s = s.replace("StrictBool", "bool")

    return s


def _normalize_type_name(annotation: typing.Any) -> str | None:
    """Normalize common typing wrappers before string fallback."""
    origin = typing.get_origin(annotation)

    if origin is typing.Annotated:
        args = typing.get_args(annotation)
        return _get_type_name(args[0]) if args else None

    if origin in (typing.Union, types.UnionType):
        return _format_union_type(annotation)

    if origin is list:
        return _format_list_type(annotation)

    if origin is dict:
        return _format_dict_type(annotation)

    if isinstance(annotation, type):
        return annotation.__name__

    return None


def _format_union_type(annotation: typing.Any) -> str:
    args = typing.get_args(annotation)
    non_none_args = [arg for arg in args if arg is not type(None)]
    if len(non_none_args) == 1:
        # Optional[T] - "optional" is already reported by field.is_required()
        return _get_type_name(non_none_args[0])
    if non_none_args:
        return " | ".join(_get_type_name(arg) for arg in non_none_args)
    return "Any"


def _format_list_type(annotation: typing.Any) -> str:
    args = typing.get_args(annotation)
    inner = _get_type_name(args[0]) if args else "Any"
    return f"List[{inner}]"


def _format_dict_type(annotation: typing.Any) -> str:
    args = typing.get_args(annotation)
    key_t = _get_type_name(args[0]) if len(args) > 0 else "Any"
    val_t = _get_type_name(args[1]) if len(args) > 1 else "Any"
    return f"Dict[{key_t}, {val_t}]"
