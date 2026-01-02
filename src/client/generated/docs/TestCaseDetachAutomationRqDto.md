# TestCaseDetachAutomationRqDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status_id** | **int** |  | [optional] 
**use_scenario_from_test_result** | **bool** |  | [optional] 
**workflow_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_detach_automation_rq_dto import TestCaseDetachAutomationRqDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseDetachAutomationRqDto from a JSON string
test_case_detach_automation_rq_dto_instance = TestCaseDetachAutomationRqDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseDetachAutomationRqDto.to_json())

# convert the object into a dict
test_case_detach_automation_rq_dto_dict = test_case_detach_automation_rq_dto_instance.to_dict()
# create an instance of TestCaseDetachAutomationRqDto from a dict
test_case_detach_automation_rq_dto_from_dict = TestCaseDetachAutomationRqDto.from_dict(test_case_detach_automation_rq_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


