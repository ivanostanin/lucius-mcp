# LaunchTestPlanAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**env_var_value_sets** | [**List[EnvironmentSetDto]**](EnvironmentSetDto.md) |  | [optional] 
**test_plan_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_test_plan_add_dto import LaunchTestPlanAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchTestPlanAddDto from a JSON string
launch_test_plan_add_dto_instance = LaunchTestPlanAddDto.from_json(json)
# print the JSON string representation of the object
print(LaunchTestPlanAddDto.to_json())

# convert the object into a dict
launch_test_plan_add_dto_dict = launch_test_plan_add_dto_instance.to_dict()
# create an instance of LaunchTestPlanAddDto from a dict
launch_test_plan_add_dto_from_dict = LaunchTestPlanAddDto.from_dict(launch_test_plan_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


