# LaunchPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**autoclose** | **bool** |  | [optional] 
**external** | **bool** |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**name** | **str** |  | [optional] 
**tags** | [**List[LaunchTagDto]**](LaunchTagDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_patch_dto import LaunchPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchPatchDto from a JSON string
launch_patch_dto_instance = LaunchPatchDto.from_json(json)
# print the JSON string representation of the object
print(LaunchPatchDto.to_json())

# convert the object into a dict
launch_patch_dto_dict = launch_patch_dto_instance.to_dict()
# create an instance of LaunchPatchDto from a dict
launch_patch_dto_from_dict = LaunchPatchDto.from_dict(launch_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


