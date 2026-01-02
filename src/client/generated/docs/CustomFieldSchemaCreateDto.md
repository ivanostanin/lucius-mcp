# CustomFieldSchemaCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_field_id** | **int** |  | 
**key** | **str** |  | 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.custom_field_schema_create_dto import CustomFieldSchemaCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldSchemaCreateDto from a JSON string
custom_field_schema_create_dto_instance = CustomFieldSchemaCreateDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldSchemaCreateDto.to_json())

# convert the object into a dict
custom_field_schema_create_dto_dict = custom_field_schema_create_dto_instance.to_dict()
# create an instance of CustomFieldSchemaCreateDto from a dict
custom_field_schema_create_dto_from_dict = CustomFieldSchemaCreateDto.from_dict(custom_field_schema_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


