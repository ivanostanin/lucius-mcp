# TestKeySchemaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**integration_id** | **int** |  | [optional] 
**integration_name** | **str** |  | [optional] 
**key** | **str** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_key_schema_dto import TestKeySchemaDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestKeySchemaDto from a JSON string
test_key_schema_dto_instance = TestKeySchemaDto.from_json(json)
# print the JSON string representation of the object
print(TestKeySchemaDto.to_json())

# convert the object into a dict
test_key_schema_dto_dict = test_key_schema_dto_instance.to_dict()
# create an instance of TestKeySchemaDto from a dict
test_key_schema_dto_from_dict = TestKeySchemaDto.from_dict(test_key_schema_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


