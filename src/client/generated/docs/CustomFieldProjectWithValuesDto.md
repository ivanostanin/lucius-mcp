# CustomFieldProjectWithValuesDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field** | [**CustomFieldProjectDto**](CustomFieldProjectDto.md) |  | [optional] 
**values** | [**List[CustomFieldValueDto]**](CustomFieldValueDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_project_with_values_dto import CustomFieldProjectWithValuesDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldProjectWithValuesDto from a JSON string
custom_field_project_with_values_dto_instance = CustomFieldProjectWithValuesDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldProjectWithValuesDto.to_json())

# convert the object into a dict
custom_field_project_with_values_dto_dict = custom_field_project_with_values_dto_instance.to_dict()
# create an instance of CustomFieldProjectWithValuesDto from a dict
custom_field_project_with_values_dto_from_dict = CustomFieldProjectWithValuesDto.from_dict(custom_field_project_with_values_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


