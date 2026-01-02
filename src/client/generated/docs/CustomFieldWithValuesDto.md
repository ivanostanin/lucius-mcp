# CustomFieldWithValuesDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field** | [**CustomFieldDto**](CustomFieldDto.md) |  | [optional] 
**values** | [**List[CustomFieldValueDto]**](CustomFieldValueDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_with_values_dto import CustomFieldWithValuesDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldWithValuesDto from a JSON string
custom_field_with_values_dto_instance = CustomFieldWithValuesDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldWithValuesDto.to_json())

# convert the object into a dict
custom_field_with_values_dto_dict = custom_field_with_values_dto_instance.to_dict()
# create an instance of CustomFieldWithValuesDto from a dict
custom_field_with_values_dto_from_dict = CustomFieldWithValuesDto.from_dict(custom_field_with_values_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


