# GlobalSettingsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_create_allowed_role** | [**AllowedRoleDto**](AllowedRoleDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.global_settings_dto import GlobalSettingsDto

# TODO update the JSON string below
json = "{}"
# create an instance of GlobalSettingsDto from a JSON string
global_settings_dto_instance = GlobalSettingsDto.from_json(json)
# print the JSON string representation of the object
print(GlobalSettingsDto.to_json())

# convert the object into a dict
global_settings_dto_dict = global_settings_dto_instance.to_dict()
# create an instance of GlobalSettingsDto from a dict
global_settings_dto_from_dict = GlobalSettingsDto.from_dict(global_settings_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


