# CustomFieldValueBulkDeleteDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ids** | **List[int]** |  | 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.custom_field_value_bulk_delete_dto import CustomFieldValueBulkDeleteDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldValueBulkDeleteDto from a JSON string
custom_field_value_bulk_delete_dto_instance = CustomFieldValueBulkDeleteDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldValueBulkDeleteDto.to_json())

# convert the object into a dict
custom_field_value_bulk_delete_dto_dict = custom_field_value_bulk_delete_dto_instance.to_dict()
# create an instance of CustomFieldValueBulkDeleteDto from a dict
custom_field_value_bulk_delete_dto_from_dict = CustomFieldValueBulkDeleteDto.from_dict(custom_field_value_bulk_delete_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


