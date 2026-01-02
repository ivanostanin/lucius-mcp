# LaunchTestCasesAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignees** | **List[str]** |  | [optional] 
**env_var_value_sets** | [**List[EnvironmentSetDto]**](EnvironmentSetDto.md) |  | [optional] 
**jobs_mapping** | [**List[JobMapping]**](JobMapping.md) |  | [optional] 
**jobs_params** | [**List[JobParameterDto]**](JobParameterDto.md) |  | [optional] 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.launch_test_cases_add_dto import LaunchTestCasesAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchTestCasesAddDto from a JSON string
launch_test_cases_add_dto_instance = LaunchTestCasesAddDto.from_json(json)
# print the JSON string representation of the object
print(LaunchTestCasesAddDto.to_json())

# convert the object into a dict
launch_test_cases_add_dto_dict = launch_test_cases_add_dto_instance.to_dict()
# create an instance of LaunchTestCasesAddDto from a dict
launch_test_cases_add_dto_from_dict = LaunchTestCasesAddDto.from_dict(launch_test_cases_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


