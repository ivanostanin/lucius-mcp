# CustomFieldSchemaCountDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**mappings_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_schema_count_dto import CustomFieldSchemaCountDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldSchemaCountDto from a JSON string
custom_field_schema_count_dto_instance = CustomFieldSchemaCountDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldSchemaCountDto.to_json())

# convert the object into a dict
custom_field_schema_count_dto_dict = custom_field_schema_count_dto_instance.to_dict()
# create an instance of CustomFieldSchemaCountDto from a dict
custom_field_schema_count_dto_from_dict = CustomFieldSchemaCountDto.from_dict(custom_field_schema_count_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


