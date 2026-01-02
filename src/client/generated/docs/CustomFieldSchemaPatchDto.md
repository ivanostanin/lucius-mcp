# CustomFieldSchemaPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | [optional] 
**key** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_schema_patch_dto import CustomFieldSchemaPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldSchemaPatchDto from a JSON string
custom_field_schema_patch_dto_instance = CustomFieldSchemaPatchDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldSchemaPatchDto.to_json())

# convert the object into a dict
custom_field_schema_patch_dto_dict = custom_field_schema_patch_dto_instance.to_dict()
# create an instance of CustomFieldSchemaPatchDto from a dict
custom_field_schema_patch_dto_from_dict = CustomFieldSchemaPatchDto.from_dict(custom_field_schema_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


