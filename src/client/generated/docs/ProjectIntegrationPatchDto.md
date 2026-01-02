# ProjectIntegrationPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**disabled** | **bool** |  | [optional] 
**secret** | **object** |  | [optional] 
**settings** | **object** |  | [optional] 

## Example

```python
from src.client.generated.models.project_integration_patch_dto import ProjectIntegrationPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectIntegrationPatchDto from a JSON string
project_integration_patch_dto_instance = ProjectIntegrationPatchDto.from_json(json)
# print the JSON string representation of the object
print(ProjectIntegrationPatchDto.to_json())

# convert the object into a dict
project_integration_patch_dto_dict = project_integration_patch_dto_instance.to_dict()
# create an instance of ProjectIntegrationPatchDto from a dict
project_integration_patch_dto_from_dict = ProjectIntegrationPatchDto.from_dict(project_integration_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


