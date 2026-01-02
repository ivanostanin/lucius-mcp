# CustomFieldBulkArchiveDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**archive** | **bool** |  | 
**custom_field_ids** | **List[int]** |  | 

## Example

```python
from src.client.generated.models.custom_field_bulk_archive_dto import CustomFieldBulkArchiveDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldBulkArchiveDto from a JSON string
custom_field_bulk_archive_dto_instance = CustomFieldBulkArchiveDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldBulkArchiveDto.to_json())

# convert the object into a dict
custom_field_bulk_archive_dto_dict = custom_field_bulk_archive_dto_instance.to_dict()
# create an instance of CustomFieldBulkArchiveDto from a dict
custom_field_bulk_archive_dto_from_dict = CustomFieldBulkArchiveDto.from_dict(custom_field_bulk_archive_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


