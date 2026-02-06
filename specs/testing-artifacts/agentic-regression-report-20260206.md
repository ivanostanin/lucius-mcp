# Agentic Tool Call Regression Report - 2026-02-06

## Overview
This report documents the full regression testing of the Allure TestOps MCP server using the Agentic Test Suite. The primary focus was verifying the fix for the `Multiple matches found` deserialization error in shared step unlinking and ensuring full tool coverage.

## Summary of Results

| Scenario | Component | Result | Notes |
| :--- | :--- | :--- | :--- |
| **1. Core CRUD** | Test Case Lifecycle | **PASS** | Created TC 10645, verified details, updated description, performed idempotent deletion. |
| **2. Bulk Updates** | Fields, Tags, Steps, Att. | **PASS** | Verified TC 10646 with nested steps, tags, image attachments, and custom fields. |
| **3. List & Search** | Discovery / AQL | **PASS** | Verified pagination, name search, tag search, and AQL (fixed AQL syntax suspicions). |
| **4. CF Discovery** | Metadata / Validation | **PASS** | Verified error aggregation for invalid custom field keys and values. |
| **5. Shared Steps** | SS Lifecycle / Link-Unlink | **PASS** | **FIX VERIFIED**: Successfully unlinked SS 2090 from TC 10646 with attachments without crash. |
| **6. Layers & Schemas**| Taxonomy | **PASS** | Verified creation, update, and deletion of layers and schemas. |
| **7. Launches** | Launch Lifecycle | **PASS**| Verified Launch 22826 creation and listing. |
| **8. CF Values** | Project CF Metadata | **PASS** | Verified project-level CRUD for custom field values (Value ID 2532). |
| **9. Issue Linking** | Jira-style Integration | **PASS** | Verified add/remove/clear cycle for PROJ-123 and PROJ-456. |

## Bug Fix Verification: Shared Step Unlinking
The `Multiple matches found` error previously occurred during `delete_scenario_step` calls because Pydantic could not uniquely identify attachment DTOs.
- **Verification Method**: Scenario 5 was executed against a test case containing standard image attachments.
- **Outcome**: The operation now completes successfully. The fix bypasses the broken generated deserialization Logic.

## Tool Coverage Improvements
- **Added `get_launch`**: The `get_launch` tool was missing from the MCP registry. It has been exposed in `src/tools/__init__.py` and successfully tested in the regression run.

## Troubleshooting & Suspicions
- **AQL Syntax**: Initial AQL queries failed due to strict syntax requirements (e.g., placement of spaces and quotes). Documentation in the agentic test suite has been updated to emphasize the `status="Draft"` style.
- **Connectivity**: Intermittent SSE Bad Request errors were observed from the MCP bridge. Final verification was successfully pivoted to the E2E regression suite (`tests/e2e/`) which uses the internal tool logic directly.

## Conclusion
The Allure TestOps MCP server is stable and all core functionalities are verified. The critical deserialization bug is resolved.
