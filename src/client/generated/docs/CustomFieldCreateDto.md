# CustomFieldCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**required** | **bool** |  | 
**single_select** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_create_dto import CustomFieldCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldCreateDto from a JSON string
custom_field_create_dto_instance = CustomFieldCreateDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldCreateDto.to_json())

# convert the object into a dict
custom_field_create_dto_dict = custom_field_create_dto_instance.to_dict()
# create an instance of CustomFieldCreateDto from a dict
custom_field_create_dto_from_dict = CustomFieldCreateDto.from_dict(custom_field_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


