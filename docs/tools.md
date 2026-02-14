# Tool Reference

Lucius provides a suite of MCP tools categorized by feature area. All tools are optimized for AI agents and return "
Agent Hints" on failure.

## 📁 Test Case Management

| Tool                          | Description                                                 | Key Parameters                  |
|:------------------------------|:------------------------------------------------------------|:--------------------------------|
| `create_test_case`            | Create a new test case with steps, tags, and custom fields. | `name`, `steps`, `tags`         |
| `update_test_case`            | Idempotently update an existing test case.                  | `test_case_id`, `name`, `steps` |
| `delete_test_case`            | Soft-delete (archive) a test case.                          | `test_case_id`, `confirm`       |
| `get_test_case_details`       | Retrieve complete details including steps and attachments.  | `test_case_id`                  |
| `get_test_case_custom_fields` | Retrieve only custom field values for a test case.          | `test_case_id`                  |

## 🔍 Search & Discovery

| Tool                | Description                                            | Key Parameters                |
|:--------------------|:-------------------------------------------------------|:------------------------------|
| `list_test_cases`   | List test cases in a project with pagination.          | `page`, `size`, `name_filter` |
| `search_test_cases` | Advanced search using simple query or AQL.             | `query`, `aql`                |
| `get_custom_fields` | List available custom fields and their allowed values. | `name` (filter)               |
| `list_integrations` | List configured issue trackers (Jira, GitHub).         | `project_id`                  |

## 🔄 Shared Steps

| Tool                 | Description                                   | Key Parameters                   |
|:---------------------|:----------------------------------------------|:---------------------------------|
| `create_shared_step` | Create a reusable sequence of steps.          | `name`, `steps`                  |
| `list_shared_steps`  | Find existing shared steps.                   | `search`, `page`                 |
| `update_shared_step` | Update an existing shared step library entry. | `step_id`, `name`                |
| `delete_shared_step` | Soft-delete (archive) a shared step.          | `step_id`, `confirm`             |
| `link_shared_step`   | Reference a shared step within a test case.   | `test_case_id`, `shared_step_id` |
| `unlink_shared_step` | Remove a shared step reference.               | `test_case_id`, `shared_step_id` |

## 🏷️ Test Layers & Custom Fields

| Tool                        | Description                                      | Key Parameters            |
|:----------------------------|:-------------------------------------------------|:--------------------------|
| `list_test_layers`          | List available test layers (Unit, E2E, etc.).    | N/A                       |
| `create_test_layer`         | Define a new taxonomy layer.                     | `name`                    |
| `update_test_layer`         | Update an existing test layer name.              | `layer_id`, `name`        |
| `delete_test_layer`         | Remove a test layer.                             | `layer_id`, `confirm`     |
| `list_test_layer_schemas`   | List automatic layer mapping schemas.            | N/A                       |
| `create_test_layer_schema`  | Create a new layer mapping schema.               | `key`, `test_layer_id`    |
| `update_test_layer_schema`  | Update an existing schema.                       | `schema_id`, `key`        |
| `delete_test_layer_schema`  | Remove a schema.                                 | `schema_id`, `confirm`    |
| `list_custom_field_values`  | List allowed values for a specific custom field. | `custom_field_id`         |
| `create_custom_field_value` | Add a new option to a custom field.              | `name`, `custom_field_id` |
| `update_custom_field_value` | Update an existing custom field value name.      | `cfv_id`, `name`          |
| `delete_custom_field_value` | Remove a custom field value option.              | `cfv_id`, `confirm`       |

## 🧭 Test Hierarchy

| Tool                         | Description                                              | Key Parameters               |
|:-----------------------------|:---------------------------------------------------------|:-----------------------------|
| `create_test_suite`          | Create a new suite node (top-level or nested) in a tree. | `name`, `tree_id`, `parent_suite_id` |
| `list_test_suites`           | List suite hierarchy for a project tree.                 | `tree_id`, `include_empty`   |
| `assign_test_cases_to_suite` | Move/attach test cases to a target suite path.           | `suite_id`, `test_case_ids`, `tree_id` |

## 🚀 Launch Management

| Tool            | Description                                        | Key Parameters |
|:----------------|:---------------------------------------------------|:---------------|
| `create_launch` | Create a new test execution launch.                | `name`, `tags` |
| `list_launches` | View recent launches and their status.             | `page`, `size` |
| `get_launch`    | Get detailed stats and defect counts for a launch. | `launch_id`    |

## 📋 Test Plan Management

| Tool                       | Description                                         | Key Parameters                              |
|:---------------------------|:----------------------------------------------------|:--------------------------------------------|
| `create_test_plan`         | Create a new test plan (manual or dynamic).         | `name`, `test_case_ids`, `aql_filter`       |
| `update_test_plan`         | Update plan metadata (name).                        | `plan_id`, `name`                           |
| `manage_test_plan_content` | Add/remove test cases or update AQL filter.         | `plan_id`, `add_ids`, `remove_ids`, `aql`   |
| `list_test_plans`          | List test plans with pagination.                    | `page`, `size`                              |
| `delete_test_plan`         | Soft-delete (archive) a test plan.                  | `plan_id`                                   |

## 🐛 Defect Management

| Tool                     | Description                                                        | Key Parameters                          |
|:-------------------------|:-------------------------------------------------------------------|:----------------------------------------|
| `create_defect`          | Create a new defect in the current project.                        | `name`, `description`                   |
| `get_defect`             | Retrieve detailed information about a specific defect.             | `defect_id`                             |
| `update_defect`          | Update a defect's name, description, or open/closed status.        | `defect_id`, `name`, `closed`           |
| `delete_defect`          | Permanently delete a defect and its matchers.                      | `defect_id`, `confirm`                  |
| `list_defects`           | List all defects in the current project.                           | N/A                                     |
| `create_defect_matcher`  | Create an automation rule to auto-link failures to a defect.       | `defect_id`, `name`, `message_regex`    |
| `update_defect_matcher`  | Update a matcher's name or regex patterns.                         | `matcher_id`, `name`, `message_regex`   |
| `delete_defect_matcher`  | Permanently delete a defect matcher.                               | `matcher_id`, `confirm`                 |
| `list_defect_matchers`   | List all matchers for a given defect.                              | `defect_id`                             |
