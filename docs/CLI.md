# Lucius CLI

## Command Model

Lucius uses an entity/action grammar:

```bash
lucius <entity>
lucius <entity> <action> --args '<json>' [--format json|table|plain]
lucius <entity> <action> --help
```

`json` is the default output format.

## Examples

```bash
# Discover actions
lucius test_case
lucius integrations

# Get action help
lucius test_case get --help
lucius launch close --help

# Execute actions
lucius test_case get --args '{"test_case_id": 1234}'
lucius test_case create --args '{"name": "Smoke login"}'
lucius launch close --args '{"launch_id": 123}' --format table
lucius defect list --args '{}' --format plain
```

## Canonical Entities

- `test_case`
- `custom_field`
- `custom_field_value`
- `launch`
- `integration`
- `shared_step`
- `test_layer`
- `test_layer_schema`
- `test_suite`
- `test_plan`
- `defect`
- `defect_matcher`

## Entity Aliases

- `integrations` -> `integration`
- `test_cases` -> `test_case`
- `launches` -> `launch`
- `shared_steps` -> `shared_step`
- `test_layers` -> `test_layer`
- `test_layer_schemas` -> `test_layer_schema`
- `test_suites` -> `test_suite`
- `test_plans` -> `test_plan`
- `defects` -> `defect`
- `defect_matchers` -> `defect_matcher`
- `custom_fields` -> `custom_field`
- `custom_field_values` -> `custom_field_value`

## Output Formats

- `--format json`
- `--format table`
- `--format plain`

Examples:

```bash
lucius test_case list --args '{}' --format json
lucius test_case list --args '{}' --format table
lucius test_case list --args '{}' --format plain
```

## Migration Notes

Legacy command style is not the primary UX anymore:

- Old: `lucius list`
- Old: `lucius call <tool_name> --args '{...}'`

Use entity/action instead:

- New: `lucius <entity>`
- New: `lucius <entity> <action> --args '{...}'`

## Help and Validation

- `lucius <entity>` prints actions and short descriptions.
- `lucius <entity> <action> --help` prints description, parameters, required/optional markers, and examples.
- Unknown entities/actions and invalid JSON receive guided error hints.
