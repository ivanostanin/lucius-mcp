# LaunchCloseConfigDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_close_filter** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**timeout_for_finished_launches** | **int** |  | [optional] 
**timeout_for_in_progress_launches** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_close_config_dto import LaunchCloseConfigDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchCloseConfigDto from a JSON string
launch_close_config_dto_instance = LaunchCloseConfigDto.from_json(json)
# print the JSON string representation of the object
print(LaunchCloseConfigDto.to_json())

# convert the object into a dict
launch_close_config_dto_dict = launch_close_config_dto_instance.to_dict()
# create an instance of LaunchCloseConfigDto from a dict
launch_close_config_dto_from_dict = LaunchCloseConfigDto.from_dict(launch_close_config_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


