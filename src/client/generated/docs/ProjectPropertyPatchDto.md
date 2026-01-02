# ProjectPropertyPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.project_property_patch_dto import ProjectPropertyPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectPropertyPatchDto from a JSON string
project_property_patch_dto_instance = ProjectPropertyPatchDto.from_json(json)
# print the JSON string representation of the object
print(ProjectPropertyPatchDto.to_json())

# convert the object into a dict
project_property_patch_dto_dict = project_property_patch_dto_instance.to_dict()
# create an instance of ProjectPropertyPatchDto from a dict
project_property_patch_dto_from_dict = ProjectPropertyPatchDto.from_dict(project_property_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


