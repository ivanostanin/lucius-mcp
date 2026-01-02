# CustomFieldSchemaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**custom_field** | [**CustomFieldDto**](CustomFieldDto.md) |  | [optional] 
**id** | **int** |  | [optional] 
**key** | **str** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.custom_field_schema_dto import CustomFieldSchemaDto

# TODO update the JSON string below
json = "{}"
# create an instance of CustomFieldSchemaDto from a JSON string
custom_field_schema_dto_instance = CustomFieldSchemaDto.from_json(json)
# print the JSON string representation of the object
print(CustomFieldSchemaDto.to_json())

# convert the object into a dict
custom_field_schema_dto_dict = custom_field_schema_dto_instance.to_dict()
# create an instance of CustomFieldSchemaDto from a dict
custom_field_schema_dto_from_dict = CustomFieldSchemaDto.from_dict(custom_field_schema_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


