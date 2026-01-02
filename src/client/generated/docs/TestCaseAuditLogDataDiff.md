# TestCaseAuditLogDataDiff


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ids** | [**DiffValueChangeSetLong**](DiffValueChangeSetLong.md) |  | [optional] 
**automated** | [**DiffValueChangeBoolean**](DiffValueChangeBoolean.md) |  | [optional] 
**deleted** | [**DiffValueChangeBoolean**](DiffValueChangeBoolean.md) |  | [optional] 
**description** | [**DiffValueChangeString**](DiffValueChangeString.md) |  | [optional] 
**description_html** | [**DiffValueChangeString**](DiffValueChangeString.md) |  | [optional] 
**expected_result** | [**DiffValueChangeString**](DiffValueChangeString.md) |  | [optional] 
**expected_result_html** | [**DiffValueChangeString**](DiffValueChangeString.md) |  | [optional] 
**full_name** | [**DiffValueChangeString**](DiffValueChangeString.md) |  | [optional] 
**name** | [**DiffValueChangeString**](DiffValueChangeString.md) |  | [optional] 
**precondition** | [**DiffValueChangeString**](DiffValueChangeString.md) |  | [optional] 
**precondition_html** | [**DiffValueChangeString**](DiffValueChangeString.md) |  | [optional] 
**project_id** | [**DiffValueChangeLong**](DiffValueChangeLong.md) |  | [optional] 
**status_id** | [**DiffValueChangeLong**](DiffValueChangeLong.md) |  | [optional] 
**test_layer_id** | [**DiffValueChangeLong**](DiffValueChangeLong.md) |  | [optional] 
**workflow_id** | [**DiffValueChangeLong**](DiffValueChangeLong.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_audit_log_data_diff import TestCaseAuditLogDataDiff

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseAuditLogDataDiff from a JSON string
test_case_audit_log_data_diff_instance = TestCaseAuditLogDataDiff.from_json(json)
# print the JSON string representation of the object
print(TestCaseAuditLogDataDiff.to_json())

# convert the object into a dict
test_case_audit_log_data_diff_dict = test_case_audit_log_data_diff_instance.to_dict()
# create an instance of TestCaseAuditLogDataDiff from a dict
test_case_audit_log_data_diff_from_dict = TestCaseAuditLogDataDiff.from_dict(test_case_audit_log_data_diff_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


