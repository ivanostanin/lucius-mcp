# CustomFieldValueProjectRenameDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_value_project_rename_dto import CustomFieldValueProjectRenameDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldValueProjectRenameDto from a JSON string
custom_field_value_project_rename_dto_instance = CustomFieldValueProjectRenameDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldValueProjectRenameDto.to_json())

# convert the object into a dict
custom_field_value_project_rename_dto_dict = custom_field_value_project_rename_dto_instance.to_dict()
# create an instance of CustomFieldValueProjectRenameDto from a dict
custom_field_value_project_rename_dto_from_dict = CustomFieldValueProjectRenameDto.from_dict(custom_field_value_project_rename_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


