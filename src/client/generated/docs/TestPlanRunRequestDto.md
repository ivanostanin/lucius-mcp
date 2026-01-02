# TestPlanRunRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**env_var_value_sets** | [**List[EnvironmentSetDto]**](EnvironmentSetDto.md) |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**launch_name** | **str** |  | 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**tags** | [**List[LaunchTagDto]**](LaunchTagDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_plan_run_request_dto import TestPlanRunRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanRunRequestDto from a JSON string
test_plan_run_request_dto_instance = TestPlanRunRequestDto.from_json(json)
# print the JSON string representation of the object
print(TestPlanRunRequestDto.to_json())

# convert the object into a dict
test_plan_run_request_dto_dict = test_plan_run_request_dto_instance.to_dict()
# create an instance of TestPlanRunRequestDto from a dict
test_plan_run_request_dto_from_dict = TestPlanRunRequestDto.from_dict(test_plan_run_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


