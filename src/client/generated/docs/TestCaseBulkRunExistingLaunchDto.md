# TestCaseBulkRunExistingLaunchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignees** | **List[str]** |  | [optional] 
**env_var_value_sets** | [**List[EnvironmentSetDto]**](EnvironmentSetDto.md) |  | [optional] 
**jobs_mapping** | [**List[JobMapping]**](JobMapping.md) |  | [optional] 
**jobs_params** | [**List[JobParameterDto]**](JobParameterDto.md) |  | [optional] 
**launch_id** | **int** |  | 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_run_existing_launch_dto import TestCaseBulkRunExistingLaunchDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkRunExistingLaunchDto from a JSON string
test_case_bulk_run_existing_launch_dto_instance = TestCaseBulkRunExistingLaunchDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkRunExistingLaunchDto.to_json())

# convert the object into a dict
test_case_bulk_run_existing_launch_dto_dict = test_case_bulk_run_existing_launch_dto_instance.to_dict()
# create an instance of TestCaseBulkRunExistingLaunchDto from a dict
test_case_bulk_run_existing_launch_dto_from_dict = TestCaseBulkRunExistingLaunchDto.from_dict(test_case_bulk_run_existing_launch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


