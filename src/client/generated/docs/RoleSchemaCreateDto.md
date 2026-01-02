# RoleSchemaCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**role_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.role_schema_create_dto import RoleSchemaCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of RoleSchemaCreateDto from a JSON string
role_schema_create_dto_instance = RoleSchemaCreateDto.from_json(json)
# print the JSON string representation of the object
print(RoleSchemaCreateDto.to_json())

# convert the object into a dict
role_schema_create_dto_dict = role_schema_create_dto_instance.to_dict()
# create an instance of RoleSchemaCreateDto from a dict
role_schema_create_dto_from_dict = RoleSchemaCreateDto.from_dict(role_schema_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


