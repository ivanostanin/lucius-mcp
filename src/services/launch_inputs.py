"""Shared validation and DTO mapping for simplified launch inputs.

Launch creation and test-plan runs accept the same simplified ``tags``,
``links``, and ``issues`` inputs. This module owns that mapping so services
reuse one implementation instead of duplicating it.
"""

from __future__ import annotations

from src.client.exceptions import AllureValidationError
from src.client.generated.models.external_link_dto import ExternalLinkDto
from src.client.generated.models.issue_dto import IssueDto
from src.client.generated.models.launch_tag_dto import LaunchTagDto

MAX_LAUNCH_NAME_LENGTH = 255
MAX_TAG_LENGTH = 255


def validate_launch_name(name: str) -> None:
    """Validate a launch name shared by launch creation and test-plan runs."""
    if not isinstance(name, str):
        raise AllureValidationError(f"Launch name must be a string, got {type(name).__name__}")
    if not name.strip():
        raise AllureValidationError("Launch name is required")
    if len(name) > MAX_LAUNCH_NAME_LENGTH:
        raise AllureValidationError(f"Launch name must be {MAX_LAUNCH_NAME_LENGTH} characters or less")


def validate_tags(tags: list[str] | None) -> None:
    """Validate simplified tag entries shared by launch creation and test-plan runs."""
    if tags is None:
        return
    if not isinstance(tags, list):
        raise AllureValidationError(f"Tags must be a list, got {type(tags).__name__}")
    for i, tag in enumerate(tags):
        if not isinstance(tag, str):
            raise AllureValidationError(f"Tag at index {i} must be a string, got {type(tag).__name__}")
        if not tag.strip():
            raise AllureValidationError(f"Tag at index {i} cannot be empty")
        if len(tag) > MAX_TAG_LENGTH:
            raise AllureValidationError(f"Tag at index {i} must be {MAX_TAG_LENGTH} characters or less")


def validate_links(links: list[dict[str, str]] | None) -> None:
    """Validate simplified external link entries shared by launch inputs."""
    if links is None:
        return
    if not isinstance(links, list):
        raise AllureValidationError(f"Links must be a list, got {type(links).__name__}")
    for i, link in enumerate(links):
        if not isinstance(link, dict):
            raise AllureValidationError(f"Link at index {i} must be a dictionary")
        if not link:
            raise AllureValidationError(f"Link at index {i} cannot be empty")
        url = link.get("url")
        if url is not None and not isinstance(url, str):
            raise AllureValidationError(f"Link at index {i} 'url' must be a string")
        name = link.get("name")
        if name is not None and not isinstance(name, str):
            raise AllureValidationError(f"Link at index {i} 'name' must be a string")
        link_type = link.get("type")
        if link_type is not None and not isinstance(link_type, str):
            raise AllureValidationError(f"Link at index {i} 'type' must be a string")


def validate_issues(issues: list[dict[str, object]] | None) -> None:
    """Validate simplified issue entries shared by launch inputs."""
    if issues is None:
        return
    if not isinstance(issues, list):
        raise AllureValidationError(f"Issues must be a list, got {type(issues).__name__}")
    for i, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise AllureValidationError(f"Issue at index {i} must be a dictionary")
        if not issue:
            raise AllureValidationError(f"Issue at index {i} cannot be empty")


def build_tag_dtos(tags: list[str] | None) -> list[LaunchTagDto] | None:
    """Map simplified tag strings to upstream launch tag DTOs."""
    if not tags:
        return None
    return [LaunchTagDto(name=tag) for tag in tags]


def build_link_dtos(links: list[dict[str, str]] | None) -> list[ExternalLinkDto] | None:
    """Map simplified link dictionaries to upstream external link DTOs."""
    if not links:
        return None
    return [ExternalLinkDto(**link) for link in links]


def build_issue_dtos(issues: list[dict[str, object]] | None) -> list[IssueDto] | None:
    """Map simplified issue dictionaries to upstream issue DTOs."""
    if not issues:
        return None
    return [IssueDto(**issue) for issue in issues]


__all__ = [
    "MAX_LAUNCH_NAME_LENGTH",
    "MAX_TAG_LENGTH",
    "build_issue_dtos",
    "build_link_dtos",
    "build_tag_dtos",
    "validate_issues",
    "validate_launch_name",
    "validate_links",
    "validate_tags",
]
