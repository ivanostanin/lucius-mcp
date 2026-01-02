# DefaultCustomFieldValueDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | 
**custom_field_value_id** | **int** |  | [optional] 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.default_custom_field_value_dto import DefaultCustomFieldValueDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefaultCustomFieldValueDto from a JSON string
default_custom_field_value_dto_instance = DefaultCustomFieldValueDto.from_json(json)
# print the JSON string representation of the object
print(DefaultCustomFieldValueDto.to_json())

# convert the object into a dict
default_custom_field_value_dto_dict = default_custom_field_value_dto_instance.to_dict()
# create an instance of DefaultCustomFieldValueDto from a dict
default_custom_field_value_dto_from_dict = DefaultCustomFieldValueDto.from_dict(default_custom_field_value_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


