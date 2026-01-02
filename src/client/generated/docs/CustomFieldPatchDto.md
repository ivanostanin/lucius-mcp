# CustomFieldPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**locked** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**required** | **bool** |  | [optional] 
**single_select** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_patch_dto import CustomFieldPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldPatchDto from a JSON string
custom_field_patch_dto_instance = CustomFieldPatchDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldPatchDto.to_json())

# convert the object into a dict
custom_field_patch_dto_dict = custom_field_patch_dto_instance.to_dict()
# create an instance of CustomFieldPatchDto from a dict
custom_field_patch_dto_from_dict = CustomFieldPatchDto.from_dict(custom_field_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


