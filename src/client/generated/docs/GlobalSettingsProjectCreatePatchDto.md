# GlobalSettingsProjectCreatePatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | [**AllowedRoleDto**](AllowedRoleDto.md) |  | 

## Example

```python
from src.client.generated.models.global_settings_project_create_patch_dto import GlobalSettingsProjectCreatePatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of GlobalSettingsProjectCreatePatchDto from a JSON string
global_settings_project_create_patch_dto_instance = GlobalSettingsProjectCreatePatchDto.from_json(json)
# print the JSON string representation of the object
print(GlobalSettingsProjectCreatePatchDto.to_json())

# convert the object into a dict
global_settings_project_create_patch_dto_dict = global_settings_project_create_patch_dto_instance.to_dict()
# create an instance of GlobalSettingsProjectCreatePatchDto from a dict
global_settings_project_create_patch_dto_from_dict = GlobalSettingsProjectCreatePatchDto.from_dict(global_settings_project_create_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


