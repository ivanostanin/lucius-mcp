# CustomFieldBulkAddToProjectsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields_ids** | **List[int]** |  | 
**projects_ids** | **List[int]** |  | 

## Example

```python
from src.client.generated.models.custom_field_bulk_add_to_projects_dto import CustomFieldBulkAddToProjectsDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldBulkAddToProjectsDto from a JSON string
custom_field_bulk_add_to_projects_dto_instance = CustomFieldBulkAddToProjectsDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldBulkAddToProjectsDto.to_json())

# convert the object into a dict
custom_field_bulk_add_to_projects_dto_dict = custom_field_bulk_add_to_projects_dto_instance.to_dict()
# create an instance of CustomFieldBulkAddToProjectsDto from a dict
custom_field_bulk_add_to_projects_dto_from_dict = CustomFieldBulkAddToProjectsDto.from_dict(custom_field_bulk_add_to_projects_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


