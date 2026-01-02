# CustomFieldValuePatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default** | **bool** |  | [optional] 
**var_global** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_value_patch_dto import CustomFieldValuePatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldValuePatchDto from a JSON string
custom_field_value_patch_dto_instance = CustomFieldValuePatchDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldValuePatchDto.to_json())

# convert the object into a dict
custom_field_value_patch_dto_dict = custom_field_value_patch_dto_instance.to_dict()
# create an instance of CustomFieldValuePatchDto from a dict
custom_field_value_patch_dto_from_dict = CustomFieldValuePatchDto.from_dict(custom_field_value_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


