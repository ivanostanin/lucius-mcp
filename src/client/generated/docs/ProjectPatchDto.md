# ProjectPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**abbr** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**favorite** | **bool** |  | [optional] 
**is_public** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.project_patch_dto import ProjectPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectPatchDto from a JSON string
project_patch_dto_instance = ProjectPatchDto.from_json(json)
# print the JSON string representation of the object
print(ProjectPatchDto.to_json())

# convert the object into a dict
project_patch_dto_dict = project_patch_dto_instance.to_dict()
# create an instance of ProjectPatchDto from a dict
project_patch_dto_from_dict = ProjectPatchDto.from_dict(project_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


