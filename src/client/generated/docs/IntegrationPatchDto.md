# IntegrationPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_project_settings** | **object** |  | [optional] 
**default_secret** | **object** |  | [optional] 
**disabled** | **bool** |  | [optional] 
**enabled_by_default** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**settings** | **object** |  | [optional] 

## Example

```python
from src.client.generated.models.integration_patch_dto import IntegrationPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationPatchDto from a JSON string
integration_patch_dto_instance = IntegrationPatchDto.from_json(json)
# print the JSON string representation of the object
print(IntegrationPatchDto.to_json())

# convert the object into a dict
integration_patch_dto_dict = integration_patch_dto_instance.to_dict()
# create an instance of IntegrationPatchDto from a dict
integration_patch_dto_from_dict = IntegrationPatchDto.from_dict(integration_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


