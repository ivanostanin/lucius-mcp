# MfaGlobalSettingsPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** |  | 

## Example

```python
from src.client.generated.models.mfa_global_settings_patch_dto import MfaGlobalSettingsPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of MfaGlobalSettingsPatchDto from a JSON string
mfa_global_settings_patch_dto_instance = MfaGlobalSettingsPatchDto.from_json(json)
# print the JSON string representation of the object
print(MfaGlobalSettingsPatchDto.to_json())

# convert the object into a dict
mfa_global_settings_patch_dto_dict = mfa_global_settings_patch_dto_instance.to_dict()
# create an instance of MfaGlobalSettingsPatchDto from a dict
mfa_global_settings_patch_dto_from_dict = MfaGlobalSettingsPatchDto.from_dict(mfa_global_settings_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


