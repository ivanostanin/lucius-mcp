# LaunchRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**closed** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**statistic** | [**List[TestStatusCount]**](TestStatusCount.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_row_dto import LaunchRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchRowDto from a JSON string
launch_row_dto_instance = LaunchRowDto.from_json(json)
# print the JSON string representation of the object
print(LaunchRowDto.to_json())

# convert the object into a dict
launch_row_dto_dict = launch_row_dto_instance.to_dict()
# create an instance of LaunchRowDto from a dict
launch_row_dto_from_dict = LaunchRowDto.from_dict(launch_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


