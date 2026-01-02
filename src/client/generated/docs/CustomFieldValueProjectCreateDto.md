# CustomFieldValueProjectCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field** | [**IdOnlyDto**](IdOnlyDto.md) |  | 
**default** | **bool** |  | [optional] 
**name** | **str** |  | 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_value_project_create_dto import CustomFieldValueProjectCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldValueProjectCreateDto from a JSON string
custom_field_value_project_create_dto_instance = CustomFieldValueProjectCreateDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldValueProjectCreateDto.to_json())

# convert the object into a dict
custom_field_value_project_create_dto_dict = custom_field_value_project_create_dto_instance.to_dict()
# create an instance of CustomFieldValueProjectCreateDto from a dict
custom_field_value_project_create_dto_from_dict = CustomFieldValueProjectCreateDto.from_dict(custom_field_value_project_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


