# LaunchLiveDocConfigDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filter** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_live_doc_config_dto import LaunchLiveDocConfigDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchLiveDocConfigDto from a JSON string
launch_live_doc_config_dto_instance = LaunchLiveDocConfigDto.from_json(json)
# print the JSON string representation of the object
print(LaunchLiveDocConfigDto.to_json())

# convert the object into a dict
launch_live_doc_config_dto_dict = launch_live_doc_config_dto_instance.to_dict()
# create an instance of LaunchLiveDocConfigDto from a dict
launch_live_doc_config_dto_from_dict = LaunchLiveDocConfigDto.from_dict(launch_live_doc_config_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


