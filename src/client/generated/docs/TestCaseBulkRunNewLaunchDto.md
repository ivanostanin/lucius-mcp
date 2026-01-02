# TestCaseBulkRunNewLaunchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignees** | **List[str]** |  | [optional] 
**env_var_value_sets** | [**List[EnvironmentSetDto]**](EnvironmentSetDto.md) |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**jobs_mapping** | [**List[JobMapping]**](JobMapping.md) |  | [optional] 
**jobs_params** | [**List[JobParameterDto]**](JobParameterDto.md) |  | [optional] 
**launch_name** | **str** |  | 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 
**tags** | [**List[LaunchTagDto]**](LaunchTagDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_bulk_run_new_launch_dto import TestCaseBulkRunNewLaunchDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkRunNewLaunchDto from a JSON string
test_case_bulk_run_new_launch_dto_instance = TestCaseBulkRunNewLaunchDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkRunNewLaunchDto.to_json())

# convert the object into a dict
test_case_bulk_run_new_launch_dto_dict = test_case_bulk_run_new_launch_dto_instance.to_dict()
# create an instance of TestCaseBulkRunNewLaunchDto from a dict
test_case_bulk_run_new_launch_dto_from_dict = TestCaseBulkRunNewLaunchDto.from_dict(test_case_bulk_run_new_launch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


