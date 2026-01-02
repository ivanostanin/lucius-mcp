# CustomFieldValueProjectMergeByNameDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | 
**default_value** | **bool** |  | 
**var_from** | **List[int]** |  | 
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.custom_field_value_project_merge_by_name_dto import CustomFieldValueProjectMergeByNameDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldValueProjectMergeByNameDto from a JSON string
custom_field_value_project_merge_by_name_dto_instance = CustomFieldValueProjectMergeByNameDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldValueProjectMergeByNameDto.to_json())

# convert the object into a dict
custom_field_value_project_merge_by_name_dto_dict = custom_field_value_project_merge_by_name_dto_instance.to_dict()
# create an instance of CustomFieldValueProjectMergeByNameDto from a dict
custom_field_value_project_merge_by_name_dto_from_dict = CustomFieldValueProjectMergeByNameDto.from_dict(custom_field_value_project_merge_by_name_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


