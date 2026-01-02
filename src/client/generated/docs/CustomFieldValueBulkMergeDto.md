# CustomFieldValueBulkMergeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | 
**default_value** | **bool** |  | 
**var_from** | **List[int]** |  | 
**name** | **str** |  | 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.custom_field_value_bulk_merge_dto import CustomFieldValueBulkMergeDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldValueBulkMergeDto from a JSON string
custom_field_value_bulk_merge_dto_instance = CustomFieldValueBulkMergeDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldValueBulkMergeDto.to_json())

# convert the object into a dict
custom_field_value_bulk_merge_dto_dict = custom_field_value_bulk_merge_dto_instance.to_dict()
# create an instance of CustomFieldValueBulkMergeDto from a dict
custom_field_value_bulk_merge_dto_from_dict = CustomFieldValueBulkMergeDto.from_dict(custom_field_value_bulk_merge_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


