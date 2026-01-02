# TestCaseAuditLogData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**diff** | [**TestCaseAuditLogDataDiff**](TestCaseAuditLogDataDiff.md) |  | [optional] 
**type** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_audit_log_data import TestCaseAuditLogData

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseAuditLogData from a JSON string
test_case_audit_log_data_instance = TestCaseAuditLogData.from_json(json)
# print the JSON string representation of the object
print(TestCaseAuditLogData.to_json())

# convert the object into a dict
test_case_audit_log_data_dict = test_case_audit_log_data_instance.to_dict()
# create an instance of TestCaseAuditLogData from a dict
test_case_audit_log_data_from_dict = TestCaseAuditLogData.from_dict(test_case_audit_log_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


