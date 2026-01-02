# CustomFieldProjectPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_custom_field_value_id** | **int** |  | [optional] 
**locked** | **bool** |  | [optional] 
**required** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_project_patch_dto import CustomFieldProjectPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldProjectPatchDto from a JSON string
custom_field_project_patch_dto_instance = CustomFieldProjectPatchDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldProjectPatchDto.to_json())

# convert the object into a dict
custom_field_project_patch_dto_dict = custom_field_project_patch_dto_instance.to_dict()
# create an instance of CustomFieldProjectPatchDto from a dict
custom_field_project_patch_dto_from_dict = CustomFieldProjectPatchDto.from_dict(custom_field_project_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


