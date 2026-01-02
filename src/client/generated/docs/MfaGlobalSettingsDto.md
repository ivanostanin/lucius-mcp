# MfaGlobalSettingsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.mfa_global_settings_dto import MfaGlobalSettingsDto

# TODO update the JSON string below
json = "{}"
# create an instance of MfaGlobalSettingsDto from a JSON string
mfa_global_settings_dto_instance = MfaGlobalSettingsDto.from_json(json)
# print the JSON string representation of the object
print(MfaGlobalSettingsDto.to_json())

# convert the object into a dict
mfa_global_settings_dto_dict = mfa_global_settings_dto_instance.to_dict()
# create an instance of MfaGlobalSettingsDto from a dict
mfa_global_settings_dto_from_dict = MfaGlobalSettingsDto.from_dict(mfa_global_settings_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


