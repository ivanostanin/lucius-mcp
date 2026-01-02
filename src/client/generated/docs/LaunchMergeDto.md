# LaunchMergeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_from** | **int** |  | 
**to** | **int** |  | 

## Example

```python
from src.client.generated.models.launch_merge_dto import LaunchMergeDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchMergeDto from a JSON string
launch_merge_dto_instance = LaunchMergeDto.from_json(json)
# print the JSON string representation of the object
print(LaunchMergeDto.to_json())

# convert the object into a dict
launch_merge_dto_dict = launch_merge_dto_instance.to_dict()
# create an instance of LaunchMergeDto from a dict
launch_merge_dto_from_dict = LaunchMergeDto.from_dict(launch_merge_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


